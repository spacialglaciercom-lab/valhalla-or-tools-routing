# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Trash Collection Route Generator GUI
"""

block_cipher = None

a = Analysis(
    ['../gui/trash_route_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'networkx',
        'gpxpy',
        'src.route_generator',
        'src.route_generator.osm_parser',
        'src.route_generator.graph_builder',
        'src.route_generator.component_analyzer',
        'src.route_generator.eulerian_solver',
        'src.route_generator.turn_optimizer',
        'src.route_generator.gpx_writer',
        'src.route_generator.report_generator',
        'src.route_generator.trash_route_generator',
        'src.route_generator.config',
        'src.route_generator.utils',
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
    name='TrashRouteGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path here
)
