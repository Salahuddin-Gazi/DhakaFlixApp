# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import get_module_file_attribute

block_cipher = None

# Comprehensive hidden imports for all dependencies
hiddenimports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.sip',

    # aiohttp and dependencies
    'aiohttp',
    'aiohttp.web',
    'aiohttp.client',
    'yarl',
    'multidict',
    'aiosignal',
    'frozenlist',
    'attrs',
    'attr',
    'charset_normalizer',
    'urllib3',

    # Database
    'sqlite3',
    'pysqlite3',

    # Web scraping
    'bs4',
    'beautifulsoup4',

    # HTTP
    'requests',
    'urllib',
    'urllib.parse',

    # mpv
    'mpv',
    'ctypes',
    'ctypes.util',
]

# Collect all data files from PyQt6
from PyInstaller.utils.hooks import get_module_file_attribute
import os

pyqt6_path = os.path.dirname(get_module_file_attribute('PyQt6'))
datas = [
    ('assets', 'assets'),
    (os.path.join(pyqt6_path, 'Qt6'), 'PyQt6/Qt6'),
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'sklearn', 'tensorflow'],
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
    name='DhakaFlixStreamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DhakaFlixStreamer'
)
