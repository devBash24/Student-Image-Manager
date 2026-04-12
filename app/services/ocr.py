from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pytesseract
from PIL import Image


def _app_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_tesseract_executable(ocr_config: dict[str, Any]) -> str | None:
    """Return an absolute path to the Tesseract binary, or None if not found."""
    candidates: list[Path] = []

    env_cmd = (os.environ.get("TESSERACT_CMD") or "").strip()
    if env_cmd:
        candidates.append(Path(env_cmd).expanduser())

    cfg_cmd = (ocr_config.get("tesseract_cmd") or "").strip()
    if cfg_cmd:
        path = Path(cfg_cmd).expanduser()
        if not path.is_absolute():
            path = _app_dir() / path
        candidates.append(path)

    which = shutil.which("tesseract")
    if which:
        candidates.append(Path(which))

    if sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        candidates.extend(
            [
                Path(program_files) / "Tesseract-OCR" / "tesseract.exe",
                Path(program_files_x86) / "Tesseract-OCR" / "tesseract.exe",
            ]
        )

    seen: set[str] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        if resolved.is_file():
            return str(resolved)
    return None


class OcrService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self._tesseract_cmd = resolve_tesseract_executable(config)

    def extract_text(self, image_path: str | Path) -> str:
        if not self._tesseract_cmd:
            raise FileNotFoundError(
                "Tesseract executable not found. Install Tesseract OCR, add it to PATH, or set "
                "ocr.tesseract_cmd in config (e.g. C:\\\\Program Files\\\\Tesseract-OCR\\\\tesseract.exe) "
                "or the TESSERACT_CMD environment variable."
            )
        previous = pytesseract.pytesseract.tesseract_cmd
        pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd
        try:
            image = Image.open(image_path)
            prepared = self._prepare_image(image)
            return pytesseract.image_to_string(
                prepared,
                config=self.config.get("tesseract_config", "--psm 6"),
            )
        finally:
            pytesseract.pytesseract.tesseract_cmd = previous

    def _prepare_image(self, image: Image.Image) -> Image.Image:
        image = image.convert("RGB")
        width, height = image.size
        crop_ratio = float(self.config.get("crop_bottom_ratio", 0.28))
        crop_ratio = min(max(crop_ratio, 0.05), 1.0)
        top = int(height * (1 - crop_ratio))
        cropped = image.crop((0, top, width, height))

        array = cv2.cvtColor(np.array(cropped), cv2.COLOR_RGB2GRAY)
        array = cv2.medianBlur(array, 3)
        threshold = int(self.config.get("threshold", 150))
        _, array = cv2.threshold(array, threshold, 255, cv2.THRESH_BINARY)
        return Image.fromarray(array)
