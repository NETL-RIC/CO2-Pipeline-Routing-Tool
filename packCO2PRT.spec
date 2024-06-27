# -*- mode: python ; coding: utf-8 -*-

import os
import sys 
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None

# Add any data that need to be copied into the pyinstaller bundle
more_datas = [
    ('Flask/cost_surfaces', 'cost_surfaces'),
    ('Flask/raster','raster'),
    ('Flask/report_builder/inputs','report_builder/inputs'),
    ('Flask/report_builder/images','report_builder/images')
    ]

a = Analysis(
    ['CO2PRT.py'],
    pathex=['./Flask'],
    binaries=[],
    datas=more_datas,
    # Add any imports that show up as missing once bundled
    hiddenimports=[
        'fiona._shim',
        'fiona.schema',
        'fiona.enums',
        'fiona.schema',
        'six',
        'scipy.special._cdflib',
        'skimage.data._fetchers',
        'skimage.graph.mcp',
        'skimage.transform._warps',
        'skimage.measure.block',
        'tqdm'
        ],
    hookspath=["."],
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
    a.binaries, # Comment in for singlefile
    a.zipfiles, # Comment in for singlefile
    a.datas, # Comment in for singlefile
    [],
    exclude_binaries=False, # by setting to false and removing call to COLLECT this bundles in onefile mode
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

# Comment out below for singlefile
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='CO2PRT_Flask',
# )
