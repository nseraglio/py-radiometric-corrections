# -*- mode: python ; coding: utf-8 -*-
#
# Spec for a SINGLE executable that works in two modes:
#   - With arguments  → CLI mode (console output visible)
#   - Without arguments (double-click) → GUI mode (console hidden via ctypes)
#
# Build command (run from the project root with venv active):
#   python -m PyInstaller correct_images_combined_onefile.spec

try:
    from PyInstaller.utils.hooks import copy_metadata
    _imgcorrect_metadata = copy_metadata('imgcorrect')
except Exception:
    _imgcorrect_metadata = []

a = Analysis(
    ['scripts\\correct_images_combined.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('exiftool/exiftool.exe', '.'),
        ('cfg/exiftool.cfg', 'cfg'),
        ('cfg/reg_config.ini', 'cfg'),
        ('sentera_radiometric_corrections_icon.ico', '.'),
        *_imgcorrect_metadata,
    ],
    hiddenimports=['pkg_resources.py2_warn'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageryCorrector',
    icon='sentera_radiometric_corrections_icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=True is required so CLI output is visible in the terminal.
    # In GUI mode the console window is hidden programmatically via ctypes.
    console=True,
)
