from __future__ import annotations

import base64
import mimetypes
import json
import os
import sys
import threading
from pathlib import Path
from typing import Any

import webview

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.processor import BatchProcessor, ProcessingCallbacks


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config" / "config.json"
UI_PATH = APP_DIR / "ui" / "index.html"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)


class Api:
    def __init__(self) -> None:
        self._window: webview.Window | None = None
        self._processor: BatchProcessor | None = None
        self._worker: threading.Thread | None = None
        self._last_output_folder: str | None = None

    def get_config(self) -> dict[str, Any]:
        return load_config()

    def save_config(self, config: dict[str, Any]) -> dict[str, Any]:
        save_config(config)
        return {"ok": True, "config": config}

    def select_image_folder(self) -> str | None:
        if not self._window:
            return None
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def select_excel_file(self) -> str | None:
        if not self._window:
            return None
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=("Excel files (*.xlsx;*.xls)", "All files (*.*)"),
        )
        return result[0] if result else None

    def select_output_folder(self) -> str | None:
        if not self._window:
            return None
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def get_image_data_url(self, image_path: str) -> dict[str, Any]:
        path = Path(image_path)
        if not path.is_file():
            return {"ok": False, "error": "image_missing"}
        mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        with path.open("rb") as file:
            encoded = base64.b64encode(file.read()).decode("ascii")
        return {"ok": True, "src": f"data:{mime_type};base64,{encoded}", "name": path.name}

    def sample_image(self, image_folder: str, config: dict[str, Any]) -> dict[str, Any]:
        try:
            return BatchProcessor(config).sample_image(image_folder)
        except Exception as error:
            return {"ok": False, "error": type(error).__name__, "detail": str(error)}

    def start_processing(self, image_folder: str, excel_file: str, config: dict[str, Any]) -> dict[str, Any]:
        if self._worker and self._worker.is_alive():
            return {"ok": False, "error": "processing_already_running"}

        self._processor = BatchProcessor(config)

        def emit(event: str, payload: dict[str, Any]) -> None:
            if self._window:
                self._window.evaluate_js(
                    f"window.appEvents && window.appEvents({json.dumps(event)}, {json.dumps(payload, ensure_ascii=False)})"
                )

        callbacks = ProcessingCallbacks(
            on_log=lambda payload: emit("log", payload),
            on_progress=lambda payload: emit("progress", payload),
            on_done=lambda payload: emit("done", payload),
        )

        def run() -> None:
            if not self._processor:
                return
            result = self._processor.process(image_folder, excel_file, callbacks)
            self._last_output_folder = result.get("output_folder")

        self._worker = threading.Thread(target=run, daemon=True)
        self._worker.start()
        return {"ok": True}

    def stop_processing(self) -> dict[str, Any]:
        if self._processor:
            self._processor.stop()
        return {"ok": True}

    def open_output_folder(self) -> dict[str, Any]:
        if not self._last_output_folder:
            return {"ok": False, "error": "no_output_folder"}
        path = Path(self._last_output_folder)
        if not path.exists():
            return {"ok": False, "error": "output_folder_missing"}
        os.startfile(path)  # type: ignore[attr-defined]
        return {"ok": True}


if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Student Image Organizer",
        UI_PATH.as_uri(),
        js_api=api,
        min_size=(1060, 760),
    )
    api._window = window
    webview.start(debug=False)
