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

    from qt_ui_modern.main_window import MainWindow
    from qt_ui_modern.styles import GLOBAL_QSS
    from qt_ui_modern.splash import show_splash
    from qt_ui_modern import theme as t

    app = QApplication(sys.argv)
    app.setApplicationName(t.APP_NAME)
    app.setApplicationVersion(t.APP_VERSION)
    app.setStyleSheet(GLOBAL_QSS)
    app.setFont(QFont(t.FONT_BODY.split(",")[0].strip(), 10))

    splash = show_splash()
    app.processEvents()

    # Build window in background while splash visible
    win = MainWindow()
    app.processEvents()

    def reveal():
        win.show()
        splash.finish(win)

    # 600ms splash — long enough to read brand, short enough to feel snappy
    QTimer.singleShot(600, reveal)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
