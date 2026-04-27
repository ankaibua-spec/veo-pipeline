"""VEO Pipeline Pro main window — wraps legacy working tabs in Fluent sidebar."""
from __future__ import annotations
import sys
from pathlib import Path
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QButtonGroup,
    QStatusBar, QGraphicsDropShadowEffect, QSizePolicy, QScrollArea,
)

# Make tool package importable
_TOOL_ROOT = Path(__file__).resolve().parent.parent
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

from . import theme as t
from .styles import GLOBAL_QSS

# Import legacy working tabs
try:
    from tab_text_to_video import TextToVideoTab
    from tab_image_to_video import ImageToVideoTab
    from tab_idea_to_video import IdeaToVideoTab
    from tab_character_sync import CharacterSyncTab
    from tab_create_image import CreateImageTab
    from tab_grok_settings import GrokSettingsTab
    from tab_settings import SettingsTab
    from status_panel import StatusPanel
    LEGACY_OK = True
except Exception as e:
    print(f"[warn] legacy tabs not available: {e}")
    LEGACY_OK = False

# Import config dataclass + settings_manager
try:
    from qt_ui.ui import AppConfig
    from settings_manager import SettingsManager
    CONFIG_OK = True
except Exception as e:
    print(f"[warn] AppConfig not available: {e}")
    CONFIG_OK = False

from .pages import (
    Image2VideoPage, Idea2VideoPage, CharacterPage,
    CreateImagePage, GrokPage, QueuePage, HistoryPage, SettingsPage,
)


def _shadow(blur=20, alpha=60):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(blur); s.setColor(QColor(0, 0, 0, alpha)); s.setOffset(0, 4)
    return s


def card(title=None, subtitle=None) -> QFrame:
    f = QFrame(); f.setObjectName("card"); f.setGraphicsEffect(_shadow())
    layout = QVBoxLayout(f); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(12)
    if title:
        ti = QLabel(title); ti.setObjectName("cardTitle"); layout.addWidget(ti)
    if subtitle:
        st = QLabel(subtitle); st.setObjectName("cardSubtitle"); st.setWordWrap(True); layout.addWidget(st)
    return f


# --- Sidebar / TopBar / Home (same as before) ----------------

class Sidebar(QFrame):
    def __init__(self, on_nav_change):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self._on_nav = on_nav_change
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        header = QFrame(); header.setObjectName("brandHeader")
        h_layout = QVBoxLayout(header); h_layout.setContentsMargins(20, 24, 20, 20); h_layout.setSpacing(2)
        name = QLabel(t.APP_NAME); name.setObjectName("brandName")
        tagline = QLabel(f"v{t.APP_VERSION} · {t.APP_BUILD}"); tagline.setObjectName("brandTagline")
        h_layout.addWidget(name); h_layout.addWidget(tagline)
        layout.addWidget(header)

        self._group = QButtonGroup(self); self._group.setExclusive(True)
        nav = QVBoxLayout(); nav.setContentsMargins(8, 0, 8, 0); nav.setSpacing(2)
        for i, (key, label, _) in enumerate(t.NAV_ITEMS):
            btn = QPushButton(f"  {label}"); btn.setObjectName("navItem")
            btn.setCheckable(True); btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._on_nav(k))
            self._group.addButton(btn, i); nav.addWidget(btn)
            if i == 0: btn.setChecked(True)
        layout.addLayout(nav)
        layout.addStretch()

        footer = QFrame()
        f_layout = QVBoxLayout(footer); f_layout.setContentsMargins(20, 12, 20, 20); f_layout.setSpacing(4)
        author = QLabel(f"<b>{t.AUTHOR}</b>"); author.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px;")
        zalo = QLabel(f"<a href=\"{t.SUPPORT_URL}\" style=\"color:{t.PRIMARY};text-decoration:none\">Zalo {t.AUTHOR_ZALO}</a>")
        zalo.setOpenExternalLinks(True); zalo.setStyleSheet("font-size: 11px;")
        f_layout.addWidget(author); f_layout.addWidget(zalo)
        layout.addWidget(footer)


class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("topBar")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self); layout.setContentsMargins(28, 0, 28, 0); layout.setSpacing(16)
        titles = QVBoxLayout(); titles.setSpacing(2)
        self.title = QLabel("Home"); self.title.setObjectName("pageTitle")
        self.subtitle = QLabel("Welcome"); self.subtitle.setObjectName("pageSubtitle")
        titles.addWidget(self.title); titles.addWidget(self.subtitle)
        layout.addLayout(titles); layout.addStretch()
        for label in ["📁 Open Output", "🔄 Refresh", "⚙ Account"]:
            b = QPushButton(label); b.setObjectName("topAction")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(b)

    def set_page(self, title: str, subtitle: str):
        self.title.setText(title); self.subtitle.setText(subtitle)


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(28, 24, 28, 24); layout.setSpacing(20)
        hero = card()
        hl = hero.layout()
        title = QLabel(f"Welcome to {t.APP_NAME}")
        title.setStyleSheet(f"font-family: '{t.FONT_HEADING}'; font-size: 24px; font-weight: 700;")
        sub = QLabel(t.APP_TAGLINE); sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 13px;")
        hl.addWidget(title); hl.addWidget(sub)
        cta = QHBoxLayout()
        b1 = QPushButton("▶ Start Generating"); b1.setObjectName("primary")
        b2 = QPushButton("📖 Documentation")
        cta.addWidget(b1); cta.addWidget(b2); cta.addStretch()
        hl.addLayout(cta)
        layout.addWidget(hero)

        stats_row = QHBoxLayout(); stats_row.setSpacing(16)
        for label, value, color in [
            ("Videos Today", "0", t.PRIMARY),
            ("This Month", "0", t.SUCCESS),
            ("Credits Left", "—", t.WARNING),
            ("Queue", "0", t.ACCENT),
        ]:
            c = card(); cl = c.layout()
            v = QLabel(value); v.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            l = QLabel(label); l.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 12px;")
            cl.addWidget(v); cl.addWidget(l); cl.addStretch()
            stats_row.addWidget(c)
        layout.addLayout(stats_row)
        layout.addStretch()


def _wrap_legacy(widget) -> QWidget:
    """Wrap legacy tab in modern padded container."""
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.setContentsMargins(20, 16, 20, 16)
    sa = QScrollArea(); sa.setWidgetResizable(True); sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setWidget(widget)
    layout.addWidget(sa)
    return w


# --- Main Window ----------------------------------------------

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
        self._cfg = self._load_config()
        self._build()

    def _load_config(self):
        if not CONFIG_OK:
            return None
        try:
            return AppConfig.load()
        except Exception as e:
            print(f"[warn] config load: {e}")
            return None

    def _build(self):
        central = QWidget(); central.setObjectName("mainContainer")
        self.setCentralWidget(central)
        outer = QHBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)

        self.sidebar = Sidebar(self._on_nav)
        outer.addWidget(self.sidebar)

        right = QVBoxLayout(); right.setContentsMargins(0, 0, 0, 0); right.setSpacing(0)
        self.topbar = TopBar(); right.addWidget(self.topbar)

        self.stack = QStackedWidget(); self.stack.setObjectName("contentArea")

        # Wire pages — legacy if available, fallback to mockups
        self.pages = {"home": HomePage()}
        if LEGACY_OK:
            try: self.pages["text2video"] = _wrap_legacy(TextToVideoTab())
            except Exception as e: print(f"[warn] TextToVideoTab: {e}")
            try: self.pages["image2video"] = _wrap_legacy(ImageToVideoTab())
            except Exception as e: print(f"[warn] ImageToVideoTab: {e}")
            try: self.pages["idea2video"] = _wrap_legacy(IdeaToVideoTab(self._cfg))
            except Exception as e: print(f"[warn] IdeaToVideoTab: {e}")
            try: self.pages["character"] = _wrap_legacy(CharacterSyncTab())
            except Exception as e: print(f"[warn] CharacterSyncTab: {e}")
            try: self.pages["create_image"] = _wrap_legacy(CreateImageTab())
            except Exception as e: print(f"[warn] CreateImageTab: {e}")
            try: self.pages["grok"] = _wrap_legacy(GrokSettingsTab())
            except Exception as e: print(f"[warn] GrokSettingsTab: {e}")
            try: self.pages["settings"] = _wrap_legacy(SettingsTab(self._cfg))
            except Exception as e: print(f"[warn] SettingsTab: {e}")
            try: self.pages["queue"] = _wrap_legacy(StatusPanel())
            except Exception as e: print(f"[warn] StatusPanel: {e}")

        # Fallback to mockups
        fallbacks = {
            "text2video": None,  # no mockup needed; if legacy missing user reverts to run_veo_4.0.py
            "image2video": Image2VideoPage,
            "idea2video": Idea2VideoPage,
            "character": CharacterPage,
            "create_image": CreateImagePage,
            "grok": GrokPage,
            "queue": QueuePage,
            "history": HistoryPage,
            "settings": SettingsPage,
        }
        for k, cls in fallbacks.items():
            if k not in self.pages and cls is not None:
                self.pages[k] = cls()

        # History always uses new design (no legacy equivalent)
        from .pages import HistoryPage as _Hist
        self.pages["history"] = _Hist()

        for key, _, _ in t.NAV_ITEMS:
            page = self.pages.get(key)
            if page is None:
                page = QLabel(f"[{key}] page unavailable; run `run_veo_4.0.py` for legacy UI")
            self.stack.addWidget(page)
        right.addWidget(self.stack)

        right_w = QWidget(); right_w.setLayout(right)
        outer.addWidget(right_w, 1)

        sb = QStatusBar()
        legacy_status = "LEGACY OK" if LEGACY_OK else "LEGACY FAIL"
        sb.showMessage(f"Ready · {t.APP_NAME} v{t.APP_VERSION} · {legacy_status} · {t.AUTHOR}")
        self.setStatusBar(sb)

    def _on_nav(self, key: str):
        idx = [k for k, _, _ in t.NAV_ITEMS].index(key)
        self.stack.setCurrentIndex(idx)
        title, subtitle = self.PAGE_TITLES.get(key, (key, ""))
        self.topbar.set_page(title, subtitle)


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_QSS)
    f = QFont(t.FONT_BODY.split(",")[0].strip(), 10); app.setFont(f)
    w = MainWindow(); w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
