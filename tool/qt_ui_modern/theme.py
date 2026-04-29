"""Theme constants — VEO Pipeline Pro Stitch design tokens."""
from __future__ import annotations

# Brand
APP_NAME = "VEO Pipeline Pro"
APP_TAGLINE = "Professional AI Video Generation Suite"
APP_VERSION = "5.4.1"
APP_BUILD = "Commercial"
AUTHOR = "Truong Hoa"
AUTHOR_ZALO = "0345431884"
SUPPORT_URL = "https://zalo.me/0345431884"
GITHUB_URL = "https://github.com/ankaibua-spec/veo-pipeline"

# === Stitch palette (Material on dark) ===
PRIMARY = "#acc7ff"          # Soft blue — links, focused borders
PRIMARY_HOVER = "#c5d6ff"
PRIMARY_PRESSED = "#8db0f7"
PRIMARY_ACCENT = "#4F8EF7"   # Stronger blue — primary CTA fill

ACCENT = "#FF6B35"           # Orange — gen / call-to-action emphasis
SUCCESS = "#22C55E"
WARNING = "#FACC15"
ERROR = "#EF4444"

# Surfaces (Material container ladder)
BG_DARK = "#131313"          # background / surface
BG_SURFACE = "#131313"
BG_DIM = "#131313"
BG_BRIGHT = "#3a3939"
BG_CONTAINER_LOW = "#1c1b1b"
BG_CONTAINER = "#201f1f"     # default card
BG_CONTAINER_HIGH = "#2a2a2a"

# Compatibility aliases (legacy code paths read these)
BG_MID = BG_CONTAINER_LOW
BG_LIGHT = BG_BRIGHT
BG_CARD = BG_CONTAINER

# Hairline border
BORDER = "#2a2a2a"
BORDER_VARIANT = "#424753"

# Text
TEXT_PRIMARY = "#e5e2e1"
TEXT_SECONDARY = "#c2c6d5"
TEXT_MUTED = "#8c909e"

# Radii (dp)
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_XL = 24

# Typography (Inter + JetBrains Mono — bundle as Qt fonts at runtime)
FONT_HEADING = "Inter Display, Inter, Segoe UI Variable Display, Segoe UI, system-ui"
FONT_BODY = "Inter, Segoe UI Variable, Segoe UI, system-ui"
FONT_MONO = "JetBrains Mono, Cascadia Mono, Consolas, monospace"

# Sidebar items
NAV_ITEMS = [
    ("home", "Home", "house"),
    ("text2video", "Text → Video", "film"),
    ("image2video", "Image → Video", "image"),
    ("idea2video", "Idea → Video", "sparkles"),
    ("eng_auto", "Auto English", "book"),
    ("character", "Character Sync", "user"),
    ("create_image", "Create Image", "palette"),
    ("grok", "Grok Video", "robot"),
    ("queue", "Queue", "list-checks"),
    ("history", "History", "history"),
    ("settings", "Settings", "settings"),
]
