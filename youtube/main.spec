# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['CrawlerWxV1.1.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['wxPython','yt_dlp','urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas','selenium','tqdm','lxml','moviepy','numpy','pysimplegui','requests'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Youtube Crawler V1.1',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Youtube Crawler V1.1',
)
