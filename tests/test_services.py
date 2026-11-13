from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import pandas as pd
from PIL import Image

from app import paths
from app.main import Api, load_config, save_config
from app.services.ocr import OcrService, resolve_tesseract_executable
from app.services.processor import BatchProcessor, ProcessingCallbacks, derive_department, sanitize_filename_part
from app.services.validator import StudentNumberValidator


class FakeOcr:
    def __init__(self, values: dict[str, str] | None = None, errors: set[str] | None = None) -> None:
        self.values = values or {}
        self.errors = errors or set()

    def extract_text(self, image_path: str | Path) -> str:
        name = Path(image_path).name
        if name in self.errors:
            raise RuntimeError("OCR exploded")
        return self.values.get(name, "")


def test_config() -> dict[str, Any]:
    return {
        "student_number_patterns": [r"202\d{7}", r"\d{10}"],
        "department_rules": {"20": "IT", "30": "Business"},
        "excel_columns": {
            "student_no": "student_no",
            "first_name": "first_name",
            "last_name": "last_name",
            "passport_number": "passport_number",
        },
        "ocr": {"crop_bottom_ratio": 0.28, "threshold": 150, "tesseract_config": "--psm 6"},
        "output": {"mode": "copy", "folder_name": "output", "unknown_department": "Unknown"},
        "supported_extensions": [".jpg", ".jpeg", ".png"],
    }


class ServiceTests(unittest.TestCase):
    def test_validator_first_match_wins(self) -> None:
        validator = StudentNumberValidator([r"AB\d{6}", r"[A-Z]{2}\d{6}"])
        result = validator.validate("student AB123456")
        self.assertEqual(result.student_no, "AB123456")
        self.assertEqual(result.pattern, r"AB\d{6}")

    def test_department_fallback(self) -> None:
        self.assertEqual(derive_department("2020201234", {"20": "IT"}), "IT")
        self.assertEqual(derive_department("2020991234", {"20": "IT"}), "Unknown")

    def test_filename_sanitization(self) -> None:
        self.assertEqual(sanitize_filename_part("A/B:C * D"), "A_B_C_D")
        self.assertEqual(sanitize_filename_part(""), "Unknown")

    def test_excel_lookup_and_copy_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "sample.jpg"
            Image.new("RGB", (20, 20), "white").save(image)
            excel = root / "students.xlsx"
            pd.DataFrame(
                [
                    {
                        "student_no": "2020201234",
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "passport_number": "P123",
                    }
                ]
            ).to_excel(excel, index=False)

            processor = BatchProcessor(test_config(), FakeOcr({"sample.jpg": "ID 2020201234"}))  # type: ignore[arg-type]
            result = processor.process(str(root), str(excel), self.callbacks())

            self.assertTrue(result["ok"])
            self.assertEqual(result["success"], 1)
            self.assertTrue((root / "output" / "IT" / "2020201234_Lovelace_Ada_IT_P123.jpg").exists())
            self.assertTrue(image.exists())

    def test_processor_validation_and_excel_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["bad.jpg", "missing.jpg"]:
                Image.new("RGB", (20, 20), "white").save(root / name)
            excel = root / "students.xlsx"
            pd.DataFrame(
                [
                    {
                        "student_no": "2020201234",
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "passport_number": "P123",
                    }
                ]
            ).to_excel(excel, index=False)

            processor = BatchProcessor(
                test_config(),
                FakeOcr({"bad.jpg": "no number", "missing.jpg": "2020999999"}),  # type: ignore[arg-type]
            )
            result = processor.process(str(root), str(excel), self.callbacks())
            reasons = {error["reason"] for error in result["errors"]}

            self.assertEqual(result["failed"], 2)
            self.assertEqual(reasons, {"validation_failed", "excel_match_failed"})
            with (root / "output" / "errors.json").open("r", encoding="utf-8") as file:
                self.assertEqual(len(json.load(file)), 2)

    def test_explicit_output_folder_and_image_data_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "custom-output"
            image = root / "sample.png"
            Image.new("RGB", (20, 20), "white").save(image)
            excel = root / "students.xlsx"
            pd.DataFrame(
                [
                    {
                        "student_no": "2020201234",
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "passport_number": "P123",
                    }
                ]
            ).to_excel(excel, index=False)
            config = test_config()
            config["output"]["folder_path"] = str(output)

            processor = BatchProcessor(config, FakeOcr({"sample.png": "ID 2020201234"}))  # type: ignore[arg-type]
            result = processor.process(str(root), str(excel), self.callbacks())
            data_url = Api().get_image_data_url(str(image))

            self.assertTrue(result["ok"])
            self.assertTrue((output / "IT" / "2020201234_Lovelace_Ada_IT_P123.png").exists())
            self.assertEqual(data_url["name"], "sample.png")
            self.assertTrue(data_url["src"].startswith("data:image/png;base64,"))

    def test_user_config_path_uses_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {paths.CONFIG_DIR_ENV: tmp}):
                self.assertEqual(paths.user_config_path(), Path(tmp) / "config.json")

    def test_load_config_creates_user_copy_from_bundled_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_config = root / "defaults" / "config.json"
            default_config.parent.mkdir()
            default_config.write_text(json.dumps({"language": "en", "ocr": {"language": "eng"}}), encoding="utf-8")
            user_config_dir = root / "user"

            with (
                mock.patch("app.main.DEFAULT_CONFIG_PATH", default_config),
                mock.patch.dict(os.environ, {paths.CONFIG_DIR_ENV: str(user_config_dir)}),
            ):
                config = load_config()

            self.assertEqual(config["language"], "en")
            self.assertEqual(json.loads((user_config_dir / "config.json").read_text(encoding="utf-8")), config)

    def test_save_config_writes_user_config_not_bundled_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_config = root / "defaults" / "config.json"
            default_config.parent.mkdir()
            default_config.write_text(json.dumps({"language": "en"}), encoding="utf-8")
            user_config_dir = root / "user"

            with (
                mock.patch("app.main.DEFAULT_CONFIG_PATH", default_config),
                mock.patch.dict(os.environ, {paths.CONFIG_DIR_ENV: str(user_config_dir)}),
            ):
                save_config({"language": "zh-CN"})

            self.assertEqual(json.loads(default_config.read_text(encoding="utf-8")), {"language": "en"})
            self.assertEqual(json.loads((user_config_dir / "config.json").read_text(encoding="utf-8")), {"language": "zh-CN"})

    def test_ocr_resolver_finds_bundled_tesseract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tesseract = root / "Tesseract-OCR" / "tesseract.exe"
            tesseract.parent.mkdir()
            tesseract.write_text("", encoding="utf-8")

            with mock.patch("app.paths.resource_root", return_value=root):
                self.assertEqual(resolve_tesseract_executable({}), str(tesseract.resolve()))

    def test_ocr_sets_tessdata_prefix_to_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tesseract_root = root / "Tesseract-OCR"
            tesseract = tesseract_root / "tesseract.exe"
            tessdata = tesseract_root / "tessdata"
            tessdata.mkdir(parents=True)
            tesseract.write_text("", encoding="utf-8")
            (tessdata / "eng.traineddata").write_text("", encoding="utf-8")
            image = root / "sample.png"
            Image.new("RGB", (20, 20), "white").save(image)
            seen_prefix: dict[str, str | None] = {}

            def fake_image_to_string(*args: Any, **kwargs: Any) -> str:
                seen_prefix["value"] = os.environ.get("TESSDATA_PREFIX")
                return "2020201234"

            with (
                mock.patch("app.paths.resource_root", return_value=root),
                mock.patch("app.services.ocr.pytesseract.image_to_string", side_effect=fake_image_to_string),
            ):
                service = OcrService({"language": "eng", "tesseract_config": "--psm 6"})
                self.assertEqual(service.extract_text(image), "2020201234")

            self.assertEqual(seen_prefix["value"], str(tesseract_root))
            self.assertNotEqual(seen_prefix["value"], str(tessdata))

    def callbacks(self) -> ProcessingCallbacks:
        return ProcessingCallbacks(on_log=lambda payload: None, on_progress=lambda payload: None, on_done=lambda payload: None)


if __name__ == "__main__":
    unittest.main()
