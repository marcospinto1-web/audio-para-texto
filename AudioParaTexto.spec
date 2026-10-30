# -*- mode: python ; coding: utf-8 -*-

import sys

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("faster_whisper")
datas += [("work/models/base", "models/base")]
ct_datas, ct_binaries, ct_hiddenimports = collect_all("ctranslate2")
av_datas, av_binaries, av_hiddenimports = collect_all("av")

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    binaries=binaries + ct_binaries + av_binaries,
    datas=datas + ct_datas + av_datas,
    hiddenimports=hiddenimports + ct_hiddenimports + av_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Audio para Texto",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="Audio para Texto",
)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Audio para Texto.app",
        icon=None,
        bundle_identifier="com.audio-para-texto.app",
        info_plist={"NSHighResolutionCapable": True},
    )

