from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "VANTIX Student Image Organizer"
CONFIG_DIR_ENV = "VANTIX_CONFIG_DIR"


def resource_root() -> Path:
    """Return the directory containing bundled application resources."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def user_config_dir() -> Path:
    override = os.environ.get(CONFIG_DIR_ENV)
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
        return Path.home() / "AppData" / "Roaming" / APP_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "vantix-student-image-organizer"
    return Path.home() / ".config" / "vantix-student-image-organizer"


def user_config_path() -> Path:
    return user_config_dir() / "config.json"
