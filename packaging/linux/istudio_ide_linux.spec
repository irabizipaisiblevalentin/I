# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the I Studio IDE Linux desktop app.

Build (from the repository root):
    pyinstaller packaging/linux/istudio_ide_linux.spec --noconfirm --clean
"""

import os

from PyInstaller.utils.hooks import collect_submodules

from istudio.ide import __version__ as IDE_VERSION

ROOT = os.path.normpath(os.path.join(SPECPATH, "..", ".."))
SRC = os.path.join(ROOT, "src")
FRONTEND_DIST = os.path.join(ROOT, "ide", "dist")
ENTRY = os.path.join(SRC, "istudio", "ide", "main.py")

hiddenimports = []
for _pkg in ("istudio", "istudio.ide", "compiler", "vm", "isoko"):
    hiddenimports += collect_submodules(_pkg)

a = Analysis(
    [ENTRY],
    pathex=[SRC],
    binaries=[],
    datas=[(FRONTEND_DIST, "ide/dist")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IStudioIDE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name="istudio-ide",
)
