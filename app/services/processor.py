from __future__ import annotations

import json
import re
import shutil
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from app.services.ocr import OcrService
from app.services.validator import StudentNumberValidator


Callback = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class ProcessingCallbacks:
    on_log: Callback
    on_progress: Callback
    on_done: Callback


def sanitize_filename_part(value: object) -> str:
    text = "" if value is None else str(value).strip()
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("._ ")
    return text or "Unknown"


def derive_department(student_no: str, rules: dict[str, str], fallback: str = "Unknown") -> str:
    dept_prefix = student_no.strip()[4:6]
    for prefix, department in rules.items():
        if dept_prefix == prefix:
            return department
    return fallback


class BatchProcessor:
    def __init__(self, config: dict[str, Any], ocr_service: OcrService | None = None) -> None:
        self.config = config
        self.validator = StudentNumberValidator(config.get("student_number_patterns", []))
        self.ocr = ocr_service or OcrService(config.get("ocr", {}))
        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def process(self, image_folder: str, excel_file: str, callbacks: ProcessingCallbacks) -> dict[str, Any]:
        image_root = Path(image_folder)
        output_root = image_root / self.config.get("output", {}).get("folder_name", "output")
        errors: list[dict[str, Any]] = []
        processed = 0
        success = 0
        failed = 0

        try:
            images = self._find_images(image_root)
            dataframe = self._load_excel(Path(excel_file))
        except Exception as error:
            payload = {"ok": False, "error": type(error).__name__, "detail": str(error)}
            callbacks.on_done(payload)
            return payload

        total = len(images)
        callbacks.on_progress({"total": total, "processed": 0, "success": 0, "failed": 0, "percent": 0})

        for image_path in images:
            if self.stop_event.is_set():
                callbacks.on_log({"level": "info", "message": "processing_stopped"})
                break

            callbacks.on_log({"level": "info", "message": "processing_image", "image": image_path.name})
            error_record = self._process_one(image_path, dataframe, output_root)
            processed += 1

            if error_record:
                failed += 1
                errors.append(error_record)
                callbacks.on_log({"level": "error", "message": error_record["reason"], "image": image_path.name})
            else:
                success += 1
                callbacks.on_log({"level": "info", "message": "image_success", "image": image_path.name})

            percent = int((processed / total) * 100) if total else 100
            callbacks.on_progress(
                {"total": total, "processed": processed, "success": success, "failed": failed, "percent": percent}
            )

        output_root.mkdir(parents=True, exist_ok=True)
        errors_dir = output_root / "errors"
        errors_dir.mkdir(parents=True, exist_ok=True)
        for record in errors:
            src = Path(record["image"])
            if not src.is_file():
                continue
            dest = self._deduplicate_path(errors_dir / src.name)
            try:
                shutil.copy2(src, dest)
            except OSError:
                continue

        errors_path = output_root / "errors.json"
        with errors_path.open("w", encoding="utf-8") as file:
            json.dump(errors, file, indent=2, ensure_ascii=False)

        result = {
            "ok": True,
            "stopped": self.stop_event.is_set(),
            "total": total,
            "processed": processed,
            "success": success,
            "failed": failed,
            "errors": errors,
            "errors_path": str(errors_path),
            "errors_folder": str(errors_dir),
            "output_folder": str(output_root),
        }
        callbacks.on_done(result)
        return result

    def _process_one(self, image_path: Path, dataframe: pd.DataFrame, output_root: Path) -> dict[str, Any] | None:
        try:
            raw_text = self.ocr.extract_text(image_path)
        except Exception as error:
            return self._error(image_path, "ocr_failed", error)

        validation = self.validator.validate(raw_text)
        if not validation.is_valid or validation.student_no is None:
            return {"image": str(image_path), "reason": "validation_failed", "raw_text": raw_text}

        try:
            row = self._lookup_student(dataframe, validation.student_no)
        except Exception as error:
            return self._error(image_path, "excel_match_failed", error, student_no=validation.student_no)

        department = derive_department(
            validation.student_no,
            self.config.get("department_rules", {}),
            self.config.get("output", {}).get("unknown_department", "Unknown"),
        )
        filename = self._build_filename(validation.student_no, row, department, image_path.suffix)
        target_dir = output_root / sanitize_filename_part(department)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._deduplicate_path(target_dir / filename)

        try:
            shutil.copy2(image_path, target_path)
        except Exception as error:
            return self._error(image_path, "copy_failed", error, student_no=validation.student_no)

        return None

    def _find_images(self, image_folder: Path) -> list[Path]:
        if not image_folder.exists() or not image_folder.is_dir():
            raise FileNotFoundError(f"Image folder not found: {image_folder}")
        extensions = {ext.lower() for ext in self.config.get("supported_extensions", [])}
        output_folder_name = self.config.get("output", {}).get("folder_name", "output")
        images = [
            path
            for path in image_folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() in extensions
            and output_folder_name not in path.relative_to(image_folder).parts
        ]
        return sorted(images)

    def _load_excel(self, excel_file: Path) -> pd.DataFrame:
        if not excel_file.exists() or not excel_file.is_file():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")
        dataframe = pd.read_excel(excel_file, dtype=str).fillna("")
        required_columns = set(self.config.get("excel_columns", {}).values())
        missing = required_columns.difference(dataframe.columns)
        if missing:
            raise ValueError(f"Missing Excel columns: {', '.join(sorted(missing))}")
        return dataframe

    def _lookup_student(self, dataframe: pd.DataFrame, student_no: str) -> pd.Series:
        column = self.config.get("excel_columns", {}).get("student_no", "student_no")
        matches = dataframe[dataframe[column].astype(str).str.strip() == student_no]
        if matches.empty:
            raise LookupError(f"No Excel row for student number {student_no}")
        return matches.iloc[0]

    def _build_filename(self, student_no: str, row: pd.Series, department: str, suffix: str) -> str:
        columns = self.config.get("excel_columns", {})
        parts = [
            student_no,
            row[columns.get("last_name", "last_name")],
            row[columns.get("first_name", "first_name")],
            department,
            row[columns.get("passport_number", "passport_number")],
        ]
        return "_".join(sanitize_filename_part(part) for part in parts) + suffix.lower()

    def _deduplicate_path(self, path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        for index in range(1, 10000):
            candidate = path.with_name(f"{stem}_{index}{suffix}")
            if not candidate.exists():
                return candidate
        raise FileExistsError(f"Unable to find available filename for {path}")

    def _error(self, image_path: Path, reason: str, error: Exception, **extra: Any) -> dict[str, Any]:
        return {
            "image": str(image_path),
            "reason": reason,
            "error": type(error).__name__,
            "detail": str(error),
            **extra,
        }
