# -*- mode: python ; coding: utf-8 -*-

import os
import sys

import pkgutil
import rasterio

from PyInstaller.compat import is_win,is_darwin
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None

# apparently rasterio has had an import issue since 2018 
additional_packages = []
for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio."):
    additional_packages.append(package.name)

# Add any data that need to be copied into the pyinstaller bundle
more_datas = [
    ('Flask/cost_surfaces', 'cost_surfaces'),
    ('Flask/raster','raster'),
    ('Flask/build','build'),
    ('Flask/report_builder/inputs','report_builder/inputs'),
    ('Flask/report_builder/images','report_builder/images'),
    ('public/documentation', 'documentation')
    ]


if hasattr(sys, 'real_prefix'):  # check if in a virtual environment
    root_path = sys.real_prefix
else:
    root_path = sys.prefix
# - conda-specific
if is_win:
    tgt_proj_data = os.path.join('Library', 'share', 'proj')
    src_proj_data = os.path.join(root_path, 'Library', 'share', 'proj')
else:  # both linux and darwin
    tgt_proj_data = os.path.join('share', 'proj')
    src_proj_data = os.path.join(root_path, 'share', 'proj')
print(src_proj_data,'--->',tgt_proj_data)
if os.path.exists(src_proj_data):
    more_datas.append((src_proj_data, tgt_proj_data))


a = Analysis(
    ['CO2PRT.py'],
    pathex=['./Flask'],
    binaries=[],
    datas=more_datas,
    # Add any imports that show up as missing once bundled
    hiddenimports=[
        'proj',
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
        'tqdm',
        'cv2'
        ] + additional_packages,
    hookspath=["./pyinstaller_hooks"],
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
    exclude_binaries=True, #False, # by setting to false and removing call to COLLECT this bundles in onefile mode
    name='Smart_CO2_Transport',
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
    icon='public/icon.png',
)

# Comment out below for singlefile
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Smart_CO2_Transport',
)
