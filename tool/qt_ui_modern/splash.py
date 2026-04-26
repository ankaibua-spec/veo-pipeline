"""Splash screen — branded loading."""
from __future__ import annotations
import sys
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont, QLinearGradient, QPen
from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel, QProgressBar, QVBoxLayout, QWidget

from . import theme as t


class VeoSplash(QSplashScreen):
    def __init__(self):
        pix = QPixmap(640, 360)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradient bg
        g = QLinearGradient(0, 0, 640, 360)
        g.setColorAt(0, QColor("#0078D4"))
        g.setColorAt(0.5, QColor("#1F1F1F"))
        g.setColorAt(1, QColor("#FF6B35"))
        p.fillRect(pix.rect(), g)

        # Dark overlay
        p.fillRect(pix.rect(), QColor(0, 0, 0, 180))

        # Brand text
        f = QFont(t.FONT_HEADING.split(",")[0].strip(), 32, QFont.Weight.Bold)
        p.setFont(f)
        p.setPen(QColor("white"))
        p.drawText(pix.rect().adjusted(40, 80, -40, -100),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   t.APP_NAME)

        f2 = QFont(t.FONT_BODY.split(",")[0].strip(), 12)
        p.setFont(f2)
        p.setPen(QColor("#A0A0A0"))
        p.drawText(pix.rect().adjusted(40, 150, -40, -80),
                   Qt.AlignmentFlag.AlignLeft, t.APP_TAGLINE)

        # Version
        p.setPen(QColor("#707070"))
        p.drawText(pix.rect().adjusted(40, 0, -40, -20),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                   f"v{t.APP_VERSION} · {t.APP_BUILD} · {t.AUTHOR}")

        # Accent line
        pen = QPen(QColor(t.PRIMARY))
        pen.setWidth(3)
        p.setPen(pen)
        p.drawLine(40, 200, 200, 200)

        p.end()
        super().__init__(pix)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)


def show_splash(duration_ms: int = 2000) -> VeoSplash:
    """Show splash for `duration_ms`. Caller schedules main window after."""
    s = VeoSplash()
    s.show()
    s.showMessage(
        "Loading...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
        QColor("#A0A0A0"),
    )
    QApplication.processEvents()
    return s


if __name__ == "__main__":
    app = QApplication(sys.argv)
    s = show_splash()
    QTimer.singleShot(2500, app.quit)
    app.exec()
