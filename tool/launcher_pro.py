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

    # Force dark Fusion palette (overrides default light theme)
    from PyQt6.QtGui import QPalette, QColor
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1F1F1F"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#252525"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2B2B2B"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252525"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#3A3A3A"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#FF6B35"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078D4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#0078D4"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#707070"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#707070"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#707070"))
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

    # Re-apply our dark QSS AFTER MainWindow built (overrides any inline light styles)
    win.setStyleSheet(GLOBAL_QSS + """
    QWidget { color: #FFFFFF; }
    QLabel { color: #FFFFFF; background: transparent; }
    QMainWindow, QWidget#AppRoot { background: #1F1F1F; }
    QTabWidget::pane { background: #1F1F1F; border: 1px solid #404040; }
    QTabBar::tab { background: #2B2B2B; color: #A0A0A0; padding: 8px 16px; }
    QTabBar::tab:selected { background: #0078D4; color: white; }
    QPushButton { background: #3A3A3A; color: #FFFFFF; border: 1px solid #404040; border-radius: 6px; padding: 6px 14px; }
    QPushButton:hover { background: #2B2B2B; border-color: #0078D4; }
    QPushButton#Accent { background: #FF6B35; color: white; border-color: #FF6B35; font-weight: 600; }
    QPushButton#Accent:hover { background: #FF8255; }
    QPushButton#Danger { background: #EF4444; color: white; border-color: #EF4444; }
    QPushButton#Warning { background: #F59E0B; color: white; border-color: #F59E0B; }
    QPushButton#Orange { background: #FF6B35; color: white; border-color: #FF6B35; }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
        background: #3A3A3A; color: #FFFFFF; border: 1px solid #404040;
        border-radius: 6px; padding: 6px 10px;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus { border-color: #0078D4; }
    QGroupBox { color: #FFFFFF; border: 1px solid #404040; border-radius: 8px; margin-top: 12px; padding-top: 14px; }
    QGroupBox::title { color: #FFFFFF; subcontrol-origin: margin; left: 12px; padding: 0 6px; }
    QTableView, QListView, QTreeView { background: #252525; color: #FFFFFF; gridline-color: #404040; selection-background-color: #0078D4; }
    QHeaderView::section { background: #2B2B2B; color: #A0A0A0; border: none; border-bottom: 1px solid #404040; padding: 6px; }
    QFrame { background: transparent; }
    QScrollArea { background: transparent; border: none; }
    """)

    # Add toolbar buttons: Bulk Login + Drive Settings (Fluent features)
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


def _check_update_async(win, app):
    try:
        from qt_ui_modern.auto_update import check_and_prompt
        if check_and_prompt(win):
            app.quit()
    except Exception as e:
        print(f"[update] {e}")


if __name__ == "__main__":
    main()
