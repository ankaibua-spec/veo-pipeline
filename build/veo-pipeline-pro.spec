# PyInstaller spec — VEO Pipeline Pro standalone build
# Build: pyinstaller build/veo-pipeline-pro.spec
# Output: dist/VEO_Pipeline_Pro.exe (single file, no Python required)

# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

ROOT = Path(SPECPATH).parent
TOOL_DIR = ROOT / "tool"

block_cipher = None

a = Analysis(
    [str(TOOL_DIR / "launcher_pro.py")],
    pathex=[str(TOOL_DIR)],
    binaries=[],
    datas=[
        (str(TOOL_DIR / "qt_ui_modern"), "qt_ui_modern"),
        (str(TOOL_DIR / "qt_ui"), "qt_ui"),
    ],
    excludes=[
        # Trim unused stdlib + deps
        "tkinter", "test", "unittest", "doctest", "pdb",
        "PyQt6.QtNetwork", "PyQt6.QtSql", "PyQt6.QtBluetooth",
        "PyQt6.QtMultimedia", "PyQt6.QtPositioning", "PyQt6.QtSensors",
        "PyQt6.QtSerialPort", "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtQuick", "PyQt6.QtQuick3D", "PyQt6.QtQml",
        "PyQt6.QtCharts", "PyQt6.QtDataVisualization",
        "matplotlib", "numpy.tests", "scipy", "pandas", "IPython",
    ],
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        # Legacy tab modules (loaded dynamically)
        "qt_ui_modern.theme",
        "qt_ui_modern.styles",
        "qt_ui_modern.main_window",
        "qt_ui_modern.splash",
        "qt_ui_modern.pages",
        "qt_ui_modern.runtime",
        "qt_ui_modern.license_dialog",
        "qt_ui_modern.onboarding",
        "qt_ui_modern.tray",
        "qt_ui_modern.auto_update",
        "tab_text_to_video",
        "tab_image_to_video",
        "tab_idea_to_video",
        "tab_character_sync",
        "tab_create_image",
        "tab_grok_settings",
        "tab_settings",
        "status_panel",
        "branding_config",
        "settings_manager",
        "popup_theme",
        "License",
        "chrome_process_manager",
        "chrome",
        # Workflows
        "A_workflow_text_to_video",
        "A_workflow_image_to_video",
        "A_workflow_idea_to_video",
        "A_workflow_generate_image",
        "A_workflow_image_to_image",
        "A_workflow_sync_chactacter",
        "A_workflow_get_token",
        "API_text_to_video",
        "API_image_to_video",
        "API_image_to_image",
        "API_Create_image",
        "API_sync_chactacter",
        "SORA_API_UPLOAD_IMAGE",
        # Grok
        "grok_api_text_to_video",
        "grok_api_image_to_video",
        "grok_workflow_text_to_video",
        "grok_workflow_image_to_video",
        "grok_chrome_manager",
        "idea_to_video",
        "login",
        "merge+video",
        "style",
        "ui",
        "UI_main",
        "worker_run_workflow",
        "worker_run_workflow_grok",
        "workflow_run_control",
        "status_help_view",
        # Playwright
        "playwright",
        "playwright.async_api",
        "playwright.sync_api",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --onedir mode: 3-5x faster startup vs --onefile (no extraction overhead).
# Distributed as zip from CI/Releases.

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir
    name="VEO_Pipeline_Pro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "build" / "app_icon.ico") if (ROOT / "build" / "app_icon.ico").exists() else None,
    version=str(ROOT / "build" / "version_info.txt") if (ROOT / "build" / "version_info.txt").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VEO_Pipeline_Pro",
)
