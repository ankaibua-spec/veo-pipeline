"""VEO Pipeline Pro main window — wraps legacy working tabs in Fluent sidebar.

Optimizations:
- Lazy tab loading: legacy tabs imported on first nav click (saves 1-3s startup)
- Page widgets cached after first build
- No blocking imports in __init__
"""
from __future__ import annotations
import sys
import importlib
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

# Lazy: legacy tabs loaded on demand via _lazy_tab()
LEGACY_TABS = {
    "text2video":   ("tab_text_to_video",   "TextToVideoTab",   ()),
    "image2video":  ("tab_image_to_video",  "ImageToVideoTab",  ()),
    "idea2video":   ("tab_idea_to_video",   "IdeaToVideoTab",   ("config",)),
    "character":    ("tab_character_sync",  "CharacterSyncTab", ()),
    "create_image": ("tab_create_image",    "CreateImageTab",   ()),
    "grok":         ("tab_grok_settings",   "GrokSettingsTab",  ()),
    "settings":     ("tab_settings",        "SettingsTab",      ("config",)),
    "queue":        ("status_panel",        "StatusPanel",      ()),
}


def _lazy_tab(key: str, config=None):
    """Import + instantiate legacy tab on first call. Returns widget or None."""
    if key not in LEGACY_TABS:
        return None
    mod_name, cls_name, args = LEGACY_TABS[key]
    try:
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        if "config" in args:
            return cls(config)
        return cls()
    except Exception as e:
        print(f"[warn] lazy {key}: {e}")
        return None


def _lazy_config():
    try:
        from qt_ui.ui import AppConfig
        return AppConfig.load()
    except Exception as e:
        print(f"[warn] config: {e}")
        return None


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
        self._cfg = None  # lazy
        self._page_built: dict[str, bool] = {}
        self._build()

    def _ensure_config(self):
        if self._cfg is None:
            self._cfg = _lazy_config()
        return self._cfg

    def _build(self):
        central = QWidget(); central.setObjectName("mainContainer")
        self.setCentralWidget(central)
        outer = QHBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)

        self.sidebar = Sidebar(self._on_nav)
        outer.addWidget(self.sidebar)

        right = QVBoxLayout(); right.setContentsMargins(0, 0, 0, 0); right.setSpacing(0)
        self.topbar = TopBar(); right.addWidget(self.topbar)

        self.stack = QStackedWidget(); self.stack.setObjectName("contentArea")

        # Build only Home + 9 placeholder containers. Real content loaded lazily.
        self.pages: dict[str, QWidget] = {"home": HomePage()}
        for key, _, _ in t.NAV_ITEMS:
            if key == "home":
                self.stack.addWidget(self.pages[key])
                self._page_built[key] = True
                continue
            placeholder = QLabel(f"Loading {key}...")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(f"color: {t.TEXT_MUTED}; font-size: 14px;")
            self.pages[key] = placeholder
            self.stack.addWidget(placeholder)
            self._page_built[key] = False

        right.addWidget(self.stack)
        right_w = QWidget(); right_w.setLayout(right)
        outer.addWidget(right_w, 1)

        sb = QStatusBar()
        sb.showMessage(f"Ready · {t.APP_NAME} v{t.APP_VERSION} · {t.AUTHOR}")
        self.setStatusBar(sb)

    def _build_page_lazy(self, key: str):
        """Build the actual page widget on first navigation. Cached after."""
        if self._page_built.get(key):
            return

        # History keeps mockup design (no legacy equivalent)
        if key == "history":
            from .pages import HistoryPage as _Hist
            new_widget = _Hist()
        elif key in LEGACY_TABS:
            cfg = self._ensure_config() if "config" in LEGACY_TABS[key][2] else None
            tab = _lazy_tab(key, cfg)
            if tab is not None:
                new_widget = _wrap_legacy(tab)
            else:
                # Fallback to mockup if legacy fails
                new_widget = self._mockup_for(key)
        else:
            new_widget = self._mockup_for(key)

        if new_widget is None:
            new_widget = QLabel(f"[{key}] unavailable")

        # Replace placeholder in stack
        idx = [k for k, _, _ in t.NAV_ITEMS].index(key)
        old = self.stack.widget(idx)
        self.stack.removeWidget(old)
        self.stack.insertWidget(idx, new_widget)
        old.deleteLater()
        self.pages[key] = new_widget
        self._page_built[key] = True

    def _mockup_for(self, key: str):
        from .pages import (
            Image2VideoPage, Idea2VideoPage, CharacterPage,
            CreateImagePage, GrokPage, QueuePage, HistoryPage, SettingsPage,
        )
        m = {
            "image2video": Image2VideoPage, "idea2video": Idea2VideoPage,
            "character": CharacterPage, "create_image": CreateImagePage,
            "grok": GrokPage, "queue": QueuePage, "history": HistoryPage,
            "settings": SettingsPage,
        }
        cls = m.get(key)
        return cls() if cls else None

    def _on_nav(self, key: str):
        self._build_page_lazy(key)
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
