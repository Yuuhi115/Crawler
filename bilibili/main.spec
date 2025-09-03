# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_app.py','fetch_site.py','fetch_video.py','utils.py','__init__.py'],
    pathex=['.'],
    binaries=[],
    datas=[
    ('./msedgedriver.exe','.'),
    ('./stealth.min.js','.'),
    ('./app_config/common_config.txt','app_config')
    ],
    hiddenimports=['json','lxml','selenium','logging','requests','tqdm','sys','wx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas','pysimplegui','yt-dlp'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BvCrawler_v1.0.2',
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
    name='BvCrawler_v1.0.2',
)
