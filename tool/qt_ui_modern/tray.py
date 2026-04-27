"""System tray + minimize-to-background."""
from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from . import theme as t


def _tray_icon() -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(t.PRIMARY))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(4, 4, 56, 56, 12, 12)
    p.setBrush(QColor("white"))
    # "V" letter
    pts = [(20, 20), (32, 44), (44, 20), (40, 20), (32, 36), (24, 20)]
    from PyQt6.QtGui import QPolygon
    from PyQt6.QtCore import QPoint
    poly = QPolygon([QPoint(x, y) for x, y in pts])
    p.drawPolygon(poly)
    p.end()
    return QIcon(pix)


def install_tray(window, app: QApplication) -> QSystemTrayIcon:
    """Create tray icon. Closing window minimizes to tray instead of quit."""
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None

    tray = QSystemTrayIcon(_tray_icon(), parent=window)
    tray.setToolTip(t.APP_NAME)

    menu = QMenu()
    show_act = QAction("Show", parent=menu)
    show_act.triggered.connect(lambda: (window.show(), window.raise_(), window.activateWindow()))
    menu.addAction(show_act)
    menu.addSeparator()

    queue_act = QAction("Open Queue", parent=menu)
    queue_act.triggered.connect(lambda: (window.show(), window._on_nav("queue")))
    menu.addAction(queue_act)

    settings_act = QAction("Settings", parent=menu)
    settings_act.triggered.connect(lambda: (window.show(), window._on_nav("settings")))
    menu.addAction(settings_act)
    menu.addSeparator()

    quit_act = QAction("Quit", parent=menu)
    quit_act.triggered.connect(app.quit)
    menu.addAction(quit_act)

    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: (window.show(), window.raise_(), window.activateWindow())
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )
    tray.show()

    # Override window close → hide
    orig_close = window.closeEvent
    def close_to_tray(ev):
        ev.ignore()
        window.hide()
        tray.showMessage(t.APP_NAME, "Running in background. Right-click tray icon to access.", QSystemTrayIcon.MessageIcon.Information, 3000)
    window.closeEvent = close_to_tray
    return tray
