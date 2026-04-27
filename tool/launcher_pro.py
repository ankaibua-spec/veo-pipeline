"""
VEO Pipeline Pro launcher — commercial UI.

Run: python launcher_pro.py

Falls back to legacy UI on import error.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    try:
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
    except ImportError:
        print("ERROR: PyQt6 not installed. Run: pip install PyQt6")
        sys.exit(1)

    from qt_ui_modern.styles import GLOBAL_QSS
    from qt_ui_modern.splash import show_splash
    from qt_ui_modern import theme as t
    from qt_ui_modern.license_dialog import is_licensed, LicenseDialog
    from qt_ui_modern.onboarding import needs_onboarding, mark_onboarded, OnboardingWizard
    from qt_ui_modern.tray import install_tray
    from qt_ui_modern.bulk_login import BulkLoginDialog
    # Use original top-level ui.py (real source). qt_ui/ subfolder contains
    # decompiled bytecode disassembly, not valid Python — avoid.
    from ui import MainWindow, AppConfig

    app = QApplication(sys.argv)
    app.setApplicationName(t.APP_NAME)
    app.setApplicationVersion(t.APP_VERSION)

    # Force dark Fusion palette using Stitch tokens (overrides default light theme)
    from PyQt6.QtGui import QPalette, QColor
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(t.BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(t.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(t.BG_CONTAINER))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(t.BG_CONTAINER_LOW))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(t.BG_CONTAINER_HIGH))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(t.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(t.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(t.BG_CONTAINER))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(t.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(t.ACCENT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(t.PRIMARY_ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link, QColor(t.PRIMARY))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(t.TEXT_MUTED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(t.TEXT_MUTED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(t.TEXT_MUTED))
    app.setPalette(palette)

    # Stylesheet on top of palette — for fluent chrome
    app.setStyleSheet(GLOBAL_QSS)
    app.setFont(QFont(t.FONT_BODY.split(",")[0].strip(), 10))

    # License gate — bypass via VEO_BYPASS_LICENSE=1
    if not is_licensed():
        dlg = LicenseDialog()
        if dlg.exec() != dlg.DialogCode.Accepted:
            sys.exit(0)

    # First-run onboarding wizard
    if needs_onboarding():
        wiz = OnboardingWizard()
        if wiz.exec() == wiz.DialogCode.Accepted:
            data = wiz.collect()
            # If user gave drive_cred path, copy to ~/.veo_pipeline/drive_credentials.json
            cred_src = data.pop("drive_cred", "")
            if cred_src:
                try:
                    import shutil as _sh
                    from pathlib import Path as _P
                    dest = _P.home() / ".veo_pipeline" / "drive_credentials.json"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    _sh.copy2(cred_src, dest)
                except Exception as e:
                    print(f"[onboard] copy cred fail: {e}")
            mark_onboarded(data)

    splash = show_splash()
    app.processEvents()

    # Build window while splash visible (original — has working buttons)
    cfg = AppConfig.load()
    win = MainWindow(cfg)
    win.setWindowTitle(f"{t.APP_NAME} v{t.APP_VERSION}")

    # Re-apply Stitch QSS AFTER MainWindow built (overrides any inline light styles in tabs)
    win.setStyleSheet(GLOBAL_QSS + f"""
    QWidget {{ color: {t.TEXT_PRIMARY}; }}
    QLabel {{ color: {t.TEXT_PRIMARY}; background: transparent; }}
    QMainWindow, QWidget#AppRoot {{ background: {t.BG_DARK}; }}
    QTabWidget::pane {{ background: {t.BG_CONTAINER}; border: 1px solid {t.BORDER}; border-radius: {t.RADIUS_MD}px; }}
    QTabBar::tab {{ background: transparent; color: {t.TEXT_MUTED}; padding: 10px 20px; border: none; }}
    QTabBar::tab:hover {{ color: {t.TEXT_PRIMARY}; }}
    QTabBar::tab:selected {{ color: {t.TEXT_PRIMARY}; font-weight: 600; border-bottom: 2px solid {t.PRIMARY}; }}
    QPushButton {{ background: {t.BG_CONTAINER}; color: {t.TEXT_PRIMARY}; border: 1px solid {t.BORDER}; border-radius: 8px; padding: 8px 16px; }}
    QPushButton:hover {{ background: {t.BG_CONTAINER_HIGH}; border-color: {t.BORDER_VARIANT}; }}
    QPushButton#Accent {{ background: {t.ACCENT}; color: white; border-color: {t.ACCENT}; font-weight: 600; }}
    QPushButton#Accent:hover {{ background: #FF8159; border-color: #FF8159; }}
    QPushButton#Danger {{ background: rgba(239,68,68,0.15); color: {t.ERROR}; border-color: rgba(239,68,68,0.4); }}
    QPushButton#Warning {{ background: rgba(250,204,21,0.15); color: {t.WARNING}; border-color: rgba(250,204,21,0.4); }}
    QPushButton#Orange {{ background: {t.ACCENT}; color: white; border-color: {t.ACCENT}; font-weight: 600; }}
    QPushButton#Orange:hover {{ background: #FF8159; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
        background: {t.BG_CONTAINER_LOW}; color: {t.TEXT_PRIMARY}; border: 1px solid {t.BORDER};
        border-radius: 8px; padding: 8px 12px;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{ border-color: {t.PRIMARY}; }}
    QGroupBox {{ color: {t.TEXT_PRIMARY}; border: 1px solid {t.BORDER}; border-radius: 12px; margin-top: 12px; padding-top: 14px; background: {t.BG_CONTAINER}; }}
    QGroupBox::title {{ color: {t.TEXT_SECONDARY}; subcontrol-origin: margin; left: 12px; padding: 0 6px; font-weight: 600; }}
    QTableView, QListView, QTreeView {{ background: {t.BG_CONTAINER}; color: {t.TEXT_PRIMARY}; gridline-color: {t.BORDER}; selection-background-color: {t.BG_CONTAINER_HIGH}; selection-color: {t.TEXT_PRIMARY}; alternate-background-color: {t.BG_CONTAINER_LOW}; }}
    QHeaderView::section {{ background: {t.BG_CONTAINER_LOW}; color: {t.TEXT_MUTED}; border: none; border-bottom: 1px solid {t.BORDER}; padding: 8px 12px; font-weight: 600; }}
    QFrame {{ background: transparent; }}
    QScrollArea {{ background: transparent; border: none; }}
    """)

    # Add toolbar buttons: Bulk Login + Drive Settings + Check Updates
    try:
        from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout
        from qt_ui_modern.drive_settings import DriveSettingsDialog

        chrome = QWidget()
        chrome_layout = QHBoxLayout(chrome)
        chrome_layout.setContentsMargins(0, 0, 8, 0)
        chrome_layout.setSpacing(6)

        bulk_btn = QPushButton("👥 Bulk Login")
        bulk_btn.setObjectName("Accent")
        bulk_btn.clicked.connect(lambda: BulkLoginDialog(win).exec())
        chrome_layout.addWidget(bulk_btn)

        drive_btn = QPushButton("☁ Drive Sync")
        drive_btn.clicked.connect(lambda: DriveSettingsDialog(win).exec())
        chrome_layout.addWidget(drive_btn)

        update_btn = QPushButton("🔄 Update")
        update_btn.setToolTip(f"Current: v{t.APP_VERSION}. Click to check GitHub Releases for newer version.")
        update_btn.clicked.connect(lambda: _check_update_loud(win, app))
        chrome_layout.addWidget(update_btn)

        if hasattr(win, "menuBar") and win.menuBar() is not None:
            win.menuBar().setCornerWidget(chrome)
    except Exception as e:
        print(f"[chrome] inject fail: {e}")

    app.processEvents()

    install_tray(win, app)

    # Start built-in Drive sync watcher (auto-uploads new videos to configured Drive folder)
    try:
        from qt_ui_modern.drive_sync import start_background
        start_background()
    except Exception as e:
        print(f"[drive_sync] {e}")

    def reveal():
        win.show()
        splash.finish(win)
        # Check for update 1.5s after window shown (non-blocking UX)
        QTimer.singleShot(1500, lambda: _check_update_async(win, app))

    QTimer.singleShot(600, reveal)
    sys.exit(app.exec())


def _check_update_async(win, app, *, manual: bool = False):
    """Auto-trigger on startup (silent on error/no-update) OR manual click (loud)."""
    try:
        from qt_ui_modern.auto_update import check_and_prompt, check_latest
        from qt_ui_modern import theme as t

        if manual:
            # Manual: always show result
            from PyQt6.QtWidgets import QMessageBox, QApplication
            release = check_latest()
            if release is None:
                # Either up-to-date or check failed — disambiguate
                import urllib.request, json
                try:
                    req = urllib.request.Request(
                        "https://api.github.com/repos/ankaibua-spec/veo-pipeline/releases/latest",
                        headers={"User-Agent": "veo-updater"},
                    )
                    with urllib.request.urlopen(req, timeout=8) as r:
                        d = json.loads(r.read().decode())
                    latest_tag = d.get("tag_name", "?")
                    QMessageBox.information(
                        win, "Up to date",
                        f"You are on the latest version.\n\nCurrent: v{t.APP_VERSION}\nLatest: {latest_tag}",
                    )
                except Exception as e:
                    QMessageBox.warning(
                        win, "Check failed",
                        f"Cannot reach GitHub:\n{e}\n\nCheck network / firewall.",
                    )
                return

        if check_and_prompt(win):
            import os as _os
            from qt_ui_modern.auto_update import consume_exit_handle, signal_exit
            print("[update] applying — force exit for swap script")
            handle = consume_exit_handle()
            def _do_exit():
                signal_exit(handle)   # tell .bat we are gone
                _os._exit(0)
            try:
                from PyQt6.QtCore import QTimer as _QT
                _QT.singleShot(200, _do_exit)
            except Exception:
                _do_exit()
    except Exception as e:
        print(f"[update] {e}")
        if manual:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(win, "Update error", f"Unexpected error:\n{e}")


def _check_update_loud(win, app):
    """Wrapper for the toolbar button — always shows a result."""
    _check_update_async(win, app, manual=True)


if __name__ == "__main__":
    main()
