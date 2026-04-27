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
    # Use original MainWindow — has working Generate / Stop / View buttons + tab layout
    from qt_ui.ui import MainWindow, AppConfig

    app = QApplication(sys.argv)
    app.setApplicationName(t.APP_NAME)
    app.setApplicationVersion(t.APP_VERSION)
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

    # Add Bulk Login button to original UI (keep Fluent feature)
    try:
        from PyQt6.QtWidgets import QPushButton
        bulk_btn = QPushButton("👥 Bulk Login")
        bulk_btn.setObjectName("Accent")
        bulk_btn.clicked.connect(lambda: BulkLoginDialog(win).exec())
        # Inject into menubar or toolbar if present
        if hasattr(win, "menuBar") and win.menuBar() is not None:
            win.menuBar().setCornerWidget(bulk_btn)
    except Exception as e:
        print(f"[bulk] inject fail: {e}")

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
