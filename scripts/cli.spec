# -*- mode: python ; coding: utf-8 -*-
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

"""
PyInstaller spec file for AI Chat Reader CLI.
NOTE: Run from project root with: pyinstaller scripts/cli.spec
"""

import os
import time
from pathlib import Path

# Get project root - use os.getcwd() since __file__ is not available in spec context
project_root = Path(os.getcwd())

# Get version info
version_file = project_root / "VERSION"
VERSION = version_file.read_text().strip()
epoch = int(time.time())
build_num = (epoch % 100) * 1000 + (epoch // 60) % 60
FULL_VERSION = f"v{VERSION}-build-{build_num}"

block_cipher = None

script_path = project_root / "scripts" / "convert_to_html.py"

a = Analysis(
    [str(script_path)],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(version_file), "."),
        (str(project_root / "scripts" / "templates"), "templates"),
        (str(project_root / "scripts" / "assets"), "assets"),
    ],
    hiddenimports=[
        "jinja2",
        "jinja2.Environment",
        "markdown",
        "PIL",
        "PIL.Image",
        "pdfkit",
        "docx",
        "openpyxl",
        "reportlab",
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f"chat-archive-converter-{FULL_VERSION}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

