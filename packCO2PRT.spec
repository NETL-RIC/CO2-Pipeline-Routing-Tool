# -*- mode: python ; coding: utf-8 -*-

import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None

# Add any data that need to be copied into the pyinstaller bundle
more_datas = [
    ('Flask/cost_surfaces', 'cost_surfaces'),
    ('Flask/raster','raster')
    ]

a = Analysis(
    ['CO2PRT.py'],
    pathex=['./Flask'],
    binaries=[],
    datas=more_datas,
    # Add any imports that show up as missing once bundled
    hiddenimports=[
        'fiona.enums',
        'scipy.special._cdflib',
        'skimage.data._fetchers',
        'skimage.graph.mcp',
        'skimage.transform._warps',
        'skimage.measure.block'
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
    [],
    exclude_binaries=True,
    name='CO2PRT_Flask',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CO2PRT_Flask',
)
