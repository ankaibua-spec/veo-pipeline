"""Main window — VEO Pipeline Pro commercial UI.

Modern Fluent-inspired design with:
- Sidebar navigation (10 features)
- Top bar with breadcrumb + actions
- Card-based content area
- Status bar with credit balance + connection state
"""
from __future__ import annotations
import sys
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea,
    QButtonGroup, QStatusBar, QGraphicsDropShadowEffect, QSizePolicy,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
)

from . import theme as t
from .styles import GLOBAL_QSS
from .pages import (
    Image2VideoPage, Idea2VideoPage, CharacterPage,
    CreateImagePage, GrokPage, QueuePage, HistoryPage, SettingsPage,
)


def _shadow(blur=20, alpha=60):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(blur)
    s.setColor(QColor(0, 0, 0, alpha))
    s.setOffset(0, 4)
    return s


def card(title: str = None, subtitle: str = None) -> QFrame:
    """Returns a styled card frame with optional header."""
    f = QFrame()
    f.setObjectName("card")
    f.setGraphicsEffect(_shadow())
    layout = QVBoxLayout(f)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)
    if title:
        ti = QLabel(title)
        ti.setObjectName("cardTitle")
        layout.addWidget(ti)
    if subtitle:
        st = QLabel(subtitle)
        st.setObjectName("cardSubtitle")
        st.setWordWrap(True)
        layout.addWidget(st)
    return f


class Sidebar(QFrame):
    def __init__(self, on_nav_change):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self._on_nav = on_nav_change
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Brand header
        header = QFrame()
        header.setObjectName("brandHeader")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 24, 20, 20)
        h_layout.setSpacing(2)
        name = QLabel(t.APP_NAME)
        name.setObjectName("brandName")
        tagline = QLabel(f"v{t.APP_VERSION} · {t.APP_BUILD}")
        tagline.setObjectName("brandTagline")
        h_layout.addWidget(name)
        h_layout.addWidget(tagline)
        layout.addWidget(header)

        # Nav items
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        nav = QVBoxLayout()
        nav.setContentsMargins(8, 0, 8, 0)
        nav.setSpacing(2)
        for i, (key, label, icon) in enumerate(t.NAV_ITEMS):
            btn = QPushButton(f"  {label}")
            btn.setObjectName("navItem")
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._on_nav(k))
            self._group.addButton(btn, i)
            nav.addWidget(btn)
            if i == 0:
                btn.setChecked(True)
        layout.addLayout(nav)
        layout.addStretch()

        # Footer — credits + author
        footer = QFrame()
        f_layout = QVBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 20)
        f_layout.setSpacing(4)
        author = QLabel(f"<b>{t.AUTHOR}</b>")
        author.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px;")
        zalo = QLabel(f"<a href=\"{t.SUPPORT_URL}\" style=\"color:{t.PRIMARY};text-decoration:none\">Zalo {t.AUTHOR_ZALO}</a>")
        zalo.setOpenExternalLinks(True)
        zalo.setStyleSheet("font-size: 11px;")
        f_layout.addWidget(author)
        f_layout.addWidget(zalo)
        layout.addWidget(footer)


class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("topBar")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(16)

        # Title block
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.title = QLabel("Home")
        self.title.setObjectName("pageTitle")
        self.subtitle = QLabel("Welcome to VEO Pipeline Pro")
        self.subtitle.setObjectName("pageSubtitle")
        titles.addWidget(self.title)
        titles.addWidget(self.subtitle)
        layout.addLayout(titles)
        layout.addStretch()

        # Top actions
        for label in ["📁 Open Output", "🔄 Refresh", "⚙ Account"]:
            b = QPushButton(label)
            b.setObjectName("topAction")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(b)

    def set_page(self, title: str, subtitle: str):
        self.title.setText(title)
        self.subtitle.setText(subtitle)


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Hero card
        hero = card()
        hl = hero.layout()
        title = QLabel(f"Welcome to {t.APP_NAME}")
        title.setStyleSheet(f"font-family: '{t.FONT_HEADING}'; font-size: 24px; font-weight: 700;")
        sub = QLabel(t.APP_TAGLINE)
        sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 13px;")
        hl.addWidget(title)
        hl.addWidget(sub)
        cta = QHBoxLayout()
        b1 = QPushButton("▶ Start Generating")
        b1.setObjectName("primary")
        b2 = QPushButton("📖 Documentation")
        cta.addWidget(b1)
        cta.addWidget(b2)
        cta.addStretch()
        hl.addLayout(cta)
        layout.addWidget(hero)

        # Stats grid 4x cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        for label, value, color in [
            ("Videos Today", "0", t.PRIMARY),
            ("This Month", "0", t.SUCCESS),
            ("Credits Left", "—", t.WARNING),
            ("Queue", "0", t.ACCENT),
        ]:
            c = card()
            cl = c.layout()
            v = QLabel(value)
            v.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            l = QLabel(label)
            l.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 12px;")
            cl.addWidget(v)
            cl.addWidget(l)
            cl.addStretch()
            stats_row.addWidget(c)
        layout.addLayout(stats_row)

        # Quick actions row
        actions_card = card("Quick Actions", "Most-used pipelines")
        al = actions_card.layout()
        grid = QHBoxLayout()
        grid.setSpacing(12)
        for label in ["Text → Video", "Image → Video", "Idea → Video", "Character Sync"]:
            b = QPushButton(label)
            b.setMinimumHeight(48)
            grid.addWidget(b)
        al.addLayout(grid)
        layout.addWidget(actions_card)

        layout.addStretch()


class Text2VideoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Prompt card
        c = card("Prompt", "Describe the video you want to generate")
        cl = c.layout()
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("e.g. a young female English teacher saying 'Hello' clearly in classroom, photorealistic 9:16")
        self.prompt.setMinimumHeight(120)
        cl.addWidget(self.prompt)
        layout.addWidget(c)

        # Settings row
        settings = card("Settings")
        sl = settings.layout()
        row = QHBoxLayout()
        row.setSpacing(16)

        for label, w in [
            ("Model", self._mk_combo(["Veo 3.1 Quality", "Veo 3.1 Fast", "Veo 3.1 Lite"])),
            ("Aspect", self._mk_combo(["9:16 (Vertical)", "16:9 (Horizontal)", "1:1 (Square)"])),
            ("Duration", self._mk_combo(["8 seconds", "6 seconds", "4 seconds"])),
            ("Count", self._mk_spin(1, 4, 1)),
        ]:
            v = QVBoxLayout()
            v.setSpacing(4)
            lbl = QLabel(label)
            lbl.setObjectName("fieldLabel")
            v.addWidget(lbl)
            v.addWidget(w)
            row.addLayout(v)
        sl.addLayout(row)
        layout.addWidget(settings)

        # CTA
        cta_row = QHBoxLayout()
        cta_row.addStretch()
        gen_btn = QPushButton("▶ Generate Video")
        gen_btn.setObjectName("accent")
        gen_btn.setMinimumHeight(44)
        gen_btn.setMinimumWidth(200)
        cta_row.addWidget(gen_btn)
        layout.addLayout(cta_row)

        layout.addStretch()

    def _mk_combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setMinimumHeight(36)
        return c

    def _mk_spin(self, lo, hi, default):
        s = QSpinBox()
        s.setRange(lo, hi)
        s.setValue(default)
        s.setMinimumHeight(36)
        return s


class PlaceholderPage(QWidget):
    def __init__(self, name: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        c = card(name, "Coming soon — this module is under development for VEO Pipeline Pro v5.x.")
        layout.addWidget(c)
        layout.addStretch()


class MainWindow(QMainWindow):
    PAGE_TITLES = {
        "home": ("Home", "Dashboard overview"),
        "text2video": ("Text → Video", "Generate Veo3 video from text prompt"),
        "image2video": ("Image → Video", "Animate image into video"),
        "idea2video": ("Idea → Video", "Auto-script + storyboard from idea"),
        "character": ("Character Sync", "Consistent character across scenes"),
        "create_image": ("Create Image", "Image generation"),
        "grok": ("Grok Video", "X.AI Grok video gen"),
        "queue": ("Queue", "Active generation jobs"),
        "history": ("History", "Past generations"),
        "settings": ("Settings", "Account, output folder, integrations"),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{t.APP_NAME} v{t.APP_VERSION}")
        self.setMinimumSize(1200, 760)
        self.resize(1440, 880)
        self._build()

    def _build(self):
        central = QWidget()
        central.setObjectName("mainContainer")
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self._on_nav)
        outer.addWidget(self.sidebar)

        # Right panel = topbar + content
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        self.topbar = TopBar()
        right.addWidget(self.topbar)

        # Stacked content
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")
        # Pages — full Fluent design for all 10 features
        self.pages = {
            "home": HomePage(),
            "text2video": Text2VideoPage(),
            "image2video": Image2VideoPage(),
            "idea2video": Idea2VideoPage(),
            "character": CharacterPage(),
            "create_image": CreateImagePage(),
            "grok": GrokPage(),
            "queue": QueuePage(),
            "history": HistoryPage(),
            "settings": SettingsPage(),
        }
        for key, _, _ in t.NAV_ITEMS:
            if key not in self.pages:
                self.pages[key] = PlaceholderPage(self.PAGE_TITLES.get(key, (key, ""))[0])
            self.stack.addWidget(self.pages[key])
        right.addWidget(self.stack)

        right_w = QWidget()
        right_w.setLayout(right)
        outer.addWidget(right_w, 1)

        # Status bar
        sb = QStatusBar()
        sb.showMessage(f"Ready · {t.APP_NAME} v{t.APP_VERSION} · Author: {t.AUTHOR} · Zalo: {t.AUTHOR_ZALO}")
        self.setStatusBar(sb)

    def _on_nav(self, key: str):
        idx = [k for k, _, _ in t.NAV_ITEMS].index(key)
        self.stack.setCurrentIndex(idx)
        title, subtitle = self.PAGE_TITLES.get(key, (key, ""))
        self.topbar.set_page(title, subtitle)


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_QSS)
    # Default Segoe UI font at 13px for crisp text
    f = QFont(t.FONT_BODY.split(",")[0].strip(), 10)
    app.setFont(f)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
