# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import customtkinter

block_cipher = None

# 🎓 DIDATTICA: Troviamo dinamicamente il percorso di customtkinter per includerlo nella build
customtkinter_path = os.path.dirname(customtkinter.__file__)

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (customtkinter_path, 'customtkinter/'),
        ('assets/', 'assets/'),
    ],
    hiddenimports=[],
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
    name='LabInternetControl',
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
    icon='assets/logo.ico' if os.path.exists('assets/logo.ico') else None
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LabInternetControl',
)
