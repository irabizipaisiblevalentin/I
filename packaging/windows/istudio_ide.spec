# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the I Studio IDE Windows desktop app.

Build (from the repository root):
    pyinstaller packaging/windows/istudio_ide.spec --noconfirm --clean
"""

import os

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

from istudio.ide import __version__ as IDE_VERSION

ROOT = os.path.normpath(os.path.join(SPECPATH, "..", ".."))
SRC = os.path.join(ROOT, "src")
FRONTEND_DIST = os.path.join(ROOT, "ide", "dist")
ICON = os.path.join(ROOT, "packaging", "windows", "app.ico")
ENTRY = os.path.join(SRC, "istudio", "ide", "main.py")

_major, _minor, _patch = [int(p) for p in IDE_VERSION.split(".")]

hiddenimports = []
for _pkg in ("istudio", "istudio.ide", "compiler", "vm", "isoko"):
    hiddenimports += collect_submodules(_pkg)

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(_major, _minor, _patch, 0),
        prodvers=(_major, _minor, _patch, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct("CompanyName", "I Language"),
                        StringStruct("FileDescription", "I Studio IDE"),
                        StringStruct("FileVersion", IDE_VERSION),
                        StringStruct("InternalName", "IStudioIDE"),
                        StringStruct("LegalCopyright", "I Language Project"),
                        StringStruct("OriginalFilename", "IStudioIDE.exe"),
                        StringStruct("ProductName", "I Studio IDE"),
                        StringStruct("ProductVersion", IDE_VERSION),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)

a = Analysis(
    [ENTRY],
    pathex=[SRC],
    binaries=[],
    datas=[(FRONTEND_DIST, "ide/dist"), (ICON, ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "IPython", "matplotlib"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
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
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,
    version=version_info,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="istudio-ide",
)
