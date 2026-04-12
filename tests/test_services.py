from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

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
        "student_number_patterns": [r"202\d{5}", r"\d{8}"],
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
        validator = StudentNumberValidator([r"202\d{5}", r"\d{8}"])
        result = validator.validate("student 20212345 and 99999999")
        self.assertEqual(result.student_no, "20212345")
        self.assertEqual(result.pattern, r"202\d{5}")

    def test_department_fallback(self) -> None:
        self.assertEqual(derive_department("20212345", {"20": "IT"}), "IT")
        self.assertEqual(derive_department("99212345", {"20": "IT"}), "Unknown")

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
                        "student_no": "20212345",
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "passport_number": "P123",
                    }
                ]
            ).to_excel(excel, index=False)

            processor = BatchProcessor(test_config(), FakeOcr({"sample.jpg": "ID 20212345"}))  # type: ignore[arg-type]
            result = processor.process(str(root), str(excel), self.callbacks())

            self.assertTrue(result["ok"])
            self.assertEqual(result["success"], 1)
            self.assertTrue((root / "output" / "IT" / "20212345_Lovelace_Ada_IT_P123.jpg").exists())
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
                        "student_no": "20212345",
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "passport_number": "P123",
                    }
                ]
            ).to_excel(excel, index=False)

            processor = BatchProcessor(
                test_config(),
                FakeOcr({"bad.jpg": "no number", "missing.jpg": "20299999"}),  # type: ignore[arg-type]
            )
            result = processor.process(str(root), str(excel), self.callbacks())
            reasons = {error["reason"] for error in result["errors"]}

            self.assertEqual(result["failed"], 2)
            self.assertEqual(reasons, {"validation_failed", "excel_match_failed"})
            with (root / "output" / "errors.json").open("r", encoding="utf-8") as file:
                self.assertEqual(len(json.load(file)), 2)

    def callbacks(self) -> ProcessingCallbacks:
        return ProcessingCallbacks(on_log=lambda payload: None, on_progress=lambda payload: None, on_done=lambda payload: None)


if __name__ == "__main__":
    unittest.main()
