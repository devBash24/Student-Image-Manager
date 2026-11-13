# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


block_cipher = None
project_root = Path(SPECPATH).resolve()

datas = [
    (str(project_root / "app-icon.ico"), "."),
    (str(project_root / "app" / "ui"), "ui"),
    (str(project_root / "app" / "config"), "config"),
    (str(project_root / "app" / "Tesseract-OCR" / "tessdata"), "Tesseract-OCR/tessdata"),
]

binaries = [
    (str(project_root / "app" / "Tesseract-OCR" / "tesseract.exe"), "Tesseract-OCR"),
]

hiddenimports = (
    collect_submodules("cv2")
    + collect_submodules("openpyxl")
)

a = Analysis(
    [str(project_root / "app" / "main.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VANTIX Student Image Organizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "app-icon.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VANTIX Student Image Organizer",
)
