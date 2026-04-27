"""Concrete pages for VEO Pipeline Pro. Each = full Fluent design."""
from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox, QSlider,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QGraphicsDropShadowEffect, QSizePolicy, QFileDialog,
    QGroupBox, QFormLayout, QTabWidget, QProgressBar, QToolButton,
)

from . import theme as t


def _shadow(blur=20, alpha=60):
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(blur)
    s.setColor(QColor(0, 0, 0, alpha))
    s.setOffset(0, 4)
    return s


def card(title=None, subtitle=None) -> QFrame:
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


def field(label: str, widget: QWidget) -> QVBoxLayout:
    v = QVBoxLayout()
    v.setSpacing(4)
    lbl = QLabel(label)
    lbl.setObjectName("fieldLabel")
    v.addWidget(lbl)
    v.addWidget(widget)
    return v


def combo(items: list[str]) -> QComboBox:
    c = QComboBox()
    c.addItems(items)
    c.setMinimumHeight(36)
    return c


def spin(lo, hi, default) -> QSpinBox:
    s = QSpinBox()
    s.setRange(lo, hi)
    s.setValue(default)
    s.setMinimumHeight(36)
    return s


# ============ Image to Video ============
class Image2VideoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Image picker
        c = card("Source Image", "Upload still image to animate (1080x1920 or 1920x1080)")
        cl = c.layout()
        pick_row = QHBoxLayout()
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("No image selected...")
        self.img_path.setMinimumHeight(36)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)
        pick_row.addWidget(self.img_path, 1)
        pick_row.addWidget(browse)
        cl.addLayout(pick_row)

        # Drop zone preview
        drop = QFrame()
        drop.setMinimumHeight(160)
        drop.setStyleSheet(f"background:{t.BG_MID}; border:2px dashed {t.BORDER}; border-radius:8px;")
        dl = QVBoxLayout(drop)
        hint = QLabel("Drag & drop image here or click Browse")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"color:{t.TEXT_MUTED}; font-size:13px; border:none;")
        dl.addWidget(hint)
        cl.addWidget(drop)
        layout.addWidget(c)

        # Motion prompt
        c2 = card("Motion Prompt", "Describe how image should move")
        c2l = c2.layout()
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("e.g. camera slowly pans left, leaves rustle gently, soft sunlight rays")
        self.prompt.setMinimumHeight(100)
        c2l.addWidget(self.prompt)
        layout.addWidget(c2)

        # Settings
        s = card("Generation Settings")
        sl = s.layout()
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(field("Model", combo(["Veo 3.1 i2v Quality", "Veo 3.1 i2v Fast", "Veo 3.1 i2v Lite"])))
        row.addLayout(field("Duration", combo(["8 seconds", "6 seconds", "4 seconds"])))
        row.addLayout(field("Motion Strength", combo(["Subtle", "Medium", "Strong"])))
        row.addLayout(field("Count", spin(1, 4, 1)))
        sl.addLayout(row)
        layout.addWidget(s)

        cta_row = QHBoxLayout()
        cta_row.addStretch()
        b = QPushButton("▶ Animate Image")
        b.setObjectName("accent")
        b.setMinimumHeight(44)
        b.setMinimumWidth(200)
        cta_row.addWidget(b)
        layout.addLayout(cta_row)
        layout.addStretch()

    def _browse(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if f: self.img_path.setText(f)


# ============ Idea to Video ============
class Idea2VideoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        c = card("Your Idea", "AI breaks idea into scenes + auto-generates each")
        cl = c.layout()
        self.idea = QTextEdit()
        self.idea.setPlaceholderText("e.g. a 30-second commercial for new coffee brand, modern cafe vibes, target millennials")
        self.idea.setMinimumHeight(120)
        cl.addWidget(self.idea)
        layout.addWidget(c)

        # Storyboard config
        s = card("Storyboard")
        sl = s.layout()
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(field("Total Duration", combo(["15s", "30s", "45s", "60s"])))
        row.addLayout(field("Scenes", spin(2, 10, 4)))
        row.addLayout(field("Style", combo(["Cinematic", "Documentary", "Commercial", "Vlog", "Educational"])))
        row.addLayout(field("Aspect", combo(["9:16 Vertical", "16:9 Horizontal", "1:1 Square"])))
        sl.addLayout(row)
        layout.addWidget(s)

        # Voiceover
        v = card("Voiceover (optional)")
        vl = v.layout()
        vrow = QHBoxLayout()
        vrow.setSpacing(16)
        self.vo_enable = QCheckBox("Enable VO")
        vrow.addWidget(self.vo_enable)
        vrow.addLayout(field("Voice", combo(["Female · Sarah", "Female · Jenny", "Male · Brian", "Male · Tom"])))
        vrow.addLayout(field("Language", combo(["English (US)", "Vietnamese", "English (UK)"])))
        vrow.addLayout(field("Pace", combo(["Slow", "Normal", "Fast"])))
        vl.addLayout(vrow)
        layout.addWidget(v)

        cta = QHBoxLayout()
        cta.addStretch()
        plan_btn = QPushButton("Plan Scenes First")
        gen_btn = QPushButton("▶ Generate Full Video")
        gen_btn.setObjectName("accent")
        gen_btn.setMinimumHeight(44)
        gen_btn.setMinimumWidth(220)
        cta.addWidget(plan_btn)
        cta.addWidget(gen_btn)
        layout.addLayout(cta)
        layout.addStretch()


# ============ Character Sync ============
class CharacterPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        c = card("Character Library", "Reusable character profiles for consistent videos")
        cl = c.layout()
        actions = QHBoxLayout()
        new_btn = QPushButton("+ New Character")
        new_btn.setObjectName("primary")
        actions.addWidget(new_btn)
        actions.addStretch()
        actions.addWidget(QPushButton("Import"))
        actions.addWidget(QPushButton("Export"))
        cl.addLayout(actions)

        # List
        self.list = QListWidget()
        self.list.setMinimumHeight(220)
        for n in ["Sarah · English Teacher (3 ref images)", "Tom · Vlogger (5 ref images)", "Maya · Influencer (8 ref images)"]:
            QListWidgetItem(n, self.list)
        cl.addWidget(self.list)
        layout.addWidget(c)

        # Edit selected
        e = card("Edit Selected")
        el = e.layout()
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(field("Name", QLineEdit()))
        row.addLayout(field("Age range", combo(["18-25", "26-35", "36-45", "46+"])))
        row.addLayout(field("Gender", combo(["Female", "Male", "Non-binary"])))
        row.addLayout(field("Style", combo(["Casual", "Professional", "Sporty", "Elegant"])))
        el.addLayout(row)

        desc = QTextEdit()
        desc.setPlaceholderText("Description e.g. shoulder-length brown hair, warm smile, blue eyes, freckles")
        desc.setMaximumHeight(80)
        el.addWidget(desc)
        layout.addWidget(e)

        cta = QHBoxLayout()
        cta.addStretch()
        save = QPushButton("Save Character")
        save.setObjectName("primary")
        cta.addWidget(save)
        layout.addLayout(cta)
        layout.addStretch()


# ============ Create Image ============
class CreateImagePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        c = card("Image Prompt")
        cl = c.layout()
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("e.g. minimalist coffee cup on white marble, soft morning light, photorealistic")
        self.prompt.setMinimumHeight(100)
        cl.addWidget(self.prompt)

        neg = QTextEdit()
        neg.setPlaceholderText("Negative prompt (optional): blurry, distorted, watermark...")
        neg.setMaximumHeight(60)
        cl.addWidget(neg)
        layout.addWidget(c)

        s = card("Settings")
        sl = s.layout()
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(field("Model", combo(["Imagen 4 · Ultra", "Nano Banana 2", "Flux Pro 1.1", "Ideogram V3"])))
        row.addLayout(field("Aspect", combo(["1:1 Square", "9:16 Vertical", "16:9 Horizontal", "4:3", "3:4"])))
        row.addLayout(field("Quality", combo(["Standard", "High", "Ultra"])))
        row.addLayout(field("Count", spin(1, 8, 4)))
        sl.addLayout(row)
        layout.addWidget(s)

        cta = QHBoxLayout()
        cta.addStretch()
        b = QPushButton("✨ Generate Images")
        b.setObjectName("accent")
        b.setMinimumHeight(44)
        b.setMinimumWidth(200)
        cta.addWidget(b)
        layout.addLayout(cta)
        layout.addStretch()


# ============ Grok Video ============
class GrokPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Mode tabs
        m = card("Mode")
        ml = m.layout()
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: transparent; }}
            QTabBar::tab {{ background: {t.BG_MID}; padding: 8px 20px; margin-right: 4px;
                            border-radius: 6px; color: {t.TEXT_SECONDARY}; }}
            QTabBar::tab:selected {{ background: {t.PRIMARY}; color: white; }}
        """)
        tabs.addTab(self._t2v_tab(), "Text → Video")
        tabs.addTab(self._i2v_tab(), "Image → Video")
        ml.addWidget(tabs)
        layout.addWidget(m)

        # Account chip
        a = card("Grok Account")
        al = a.layout()
        row = QHBoxLayout()
        status = QLabel("● Connected")
        status.setStyleSheet(f"color: {t.SUCCESS}; font-weight: 600;")
        row.addWidget(status)
        row.addWidget(QLabel("user@x.ai · Premium+ · 12 videos remaining today"))
        row.addStretch()
        row.addWidget(QPushButton("Switch Account"))
        al.addLayout(row)
        layout.addWidget(a)
        layout.addStretch()

    def _t2v_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        prompt = QTextEdit()
        prompt.setPlaceholderText("Prompt for Grok Imagine video gen...")
        prompt.setMinimumHeight(100)
        l.addWidget(prompt)
        row = QHBoxLayout()
        row.addLayout(field("Aspect", combo(["9:16", "16:9", "1:1"])))
        row.addLayout(field("Duration", combo(["6s", "10s"])))
        row.addLayout(field("Audio", combo(["Auto", "Music only", "None"])))
        l.addLayout(row)
        cta = QHBoxLayout(); cta.addStretch()
        b = QPushButton("▶ Generate")
        b.setObjectName("accent")
        b.setMinimumHeight(40)
        cta.addWidget(b)
        l.addLayout(cta)
        return w

    def _i2v_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Image to video — drop reference image"))
        l.addStretch()
        return w


# ============ Queue ============
class QueuePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Stats
        stats = QHBoxLayout()
        stats.setSpacing(16)
        for label, val, color in [
            ("Active", "0", t.PRIMARY),
            ("Queued", "0", t.WARNING),
            ("Completed Today", "0", t.SUCCESS),
            ("Failed Today", "0", t.ERROR),
        ]:
            c = card()
            cl = c.layout()
            v = QLabel(val)
            v.setStyleSheet(f"color:{color}; font-size:24px; font-weight:700;")
            l = QLabel(label)
            l.setStyleSheet(f"color:{t.TEXT_SECONDARY}; font-size:11px;")
            cl.addWidget(v); cl.addWidget(l); cl.addStretch()
            stats.addWidget(c)
        layout.addLayout(stats)

        # Queue table
        c = card("Active Jobs")
        cl = c.layout()
        actions = QHBoxLayout()
        actions.addWidget(QPushButton("⏸ Pause All"))
        actions.addWidget(QPushButton("🗑 Clear Failed"))
        actions.addStretch()
        actions.addWidget(QPushButton("🔄 Refresh"))
        cl.addLayout(actions)

        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(["#", "Type", "Prompt", "Model", "Progress", "Status"])
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(300)
        cl.addWidget(table)
        layout.addWidget(c, 1)


# ============ History ============
class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Filter bar
        f = card("Filter")
        fl = f.layout()
        row = QHBoxLayout()
        row.addWidget(QLineEdit(placeholderText="🔍 Search prompt..."))
        row.addWidget(combo(["All Models", "Veo 3.1 Quality", "Veo 3.1 Fast", "Veo 3.1 Lite", "Grok"]))
        row.addWidget(combo(["Last 24h", "Last 7d", "Last 30d", "All time"]))
        row.addWidget(QPushButton("Export CSV"))
        fl.addLayout(row)
        layout.addWidget(f)

        # Grid of video cards
        c = card("Videos")
        cl = c.layout()
        grid = QListWidget()
        grid.setViewMode(QListWidget.ViewMode.IconMode)
        grid.setIconSize(self._thumb_size())
        grid.setSpacing(12)
        grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        grid.setMinimumHeight(380)
        cl.addWidget(grid)
        layout.addWidget(c, 1)

    def _thumb_size(self):
        from PyQt6.QtCore import QSize
        return QSize(160, 280)


# ============ Settings ============
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Account
        a = card("Account & License", "Connected Google Flow account")
        al = a.layout()
        row = QHBoxLayout()
        status = QLabel("● Active")
        status.setStyleSheet(f"color:{t.SUCCESS}; font-weight:600;")
        row.addWidget(status)
        row.addWidget(QLabel("user@example.com · ULTRA tier · 23,205 credits"))
        row.addStretch()
        row.addWidget(QPushButton("Re-login"))
        row.addWidget(QPushButton("Add Account"))
        al.addLayout(row)
        layout.addWidget(a)

        # Output paths
        o = card("Output", "Where generated videos are saved")
        ol = o.layout()
        for label in ["Video output dir", "Image output dir"]:
            row = QHBoxLayout()
            row.addLayout(field(label, QLineEdit()))
            b = QPushButton("Browse...")
            row.addWidget(b)
            ol.addLayout(row)
        layout.addWidget(o)

        # Integrations
        i = card("Integrations", "Drive sync + Telegram + Auto-update")
        il = i.layout()
        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Drive Folder ID:", QLineEdit(placeholderText="1A2b3C4d...."))
        form.addRow("Drive Service Account JSON:", QLineEdit(placeholderText="path to credentials.json"))
        form.addRow("Telegram Bot Token:", QLineEdit(placeholderText="123:ABC..."))
        form.addRow("Telegram Chat ID:", QLineEdit(placeholderText="-100123..."))
        cb = QCheckBox("Enable auto-update from GitHub every 6h")
        cb.setChecked(True)
        form.addRow("", cb)
        il.addLayout(form)
        layout.addWidget(i)

        # Save bar
        cta = QHBoxLayout()
        cta.addStretch()
        cta.addWidget(QPushButton("Reset Defaults"))
        save = QPushButton("Save Settings")
        save.setObjectName("primary")
        cta.addWidget(save)
        layout.addLayout(cta)
        layout.addStretch()
