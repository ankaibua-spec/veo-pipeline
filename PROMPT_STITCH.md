# Stitch Generation Prompts — VEO Pipeline Pro

Use these prompts at https://stitch.withgoogle.com.
Upload `DESIGN.md` first (Settings → Upload context), then paste prompt below.

---

## 🎯 Master Prompt (recommended — single shot)

```
Build a professional Windows-style desktop application UI called "VEO Pipeline Pro" — a commercial AI video generation tool. Use a Microsoft Fluent Design dark theme.

LAYOUT:
- Persistent 240px left sidebar (background #2B2B2B, 1px right border #404040)
- 56px top bar (background #1F1F1F, bottom border #404040)
- Main content area background #1F1F1F, padded 28px horizontal / 24px vertical
- Status bar at bottom (28px, background #2B2B2B)

SIDEBAR contains:
1. Brand header: "VEO Pipeline Pro" (20px bold white) + "v5.0.3 · Commercial" (11px muted #707070), 24px top padding
2. Nav items (40px height, 8px padding, 6px radius, transparent → hover #3A3A3A → active #0078D4 with white 600 weight):
   - Home, Text → Video, Image → Video, Idea → Video, Character Sync, Create Image, Grok Video, Queue, History, Settings
3. Footer: "Truong Hoa" (bold 11px #A0A0A0) + "Zalo 0345431884" (link 11px #0078D4)

TOP BAR:
- Left: page title 18px/600 white + subtitle 12px/#707070 (2px gap)
- Right: 4 secondary buttons in row (👥 Bulk Login, 📁 Open Output, 🔄 Refresh, ⚙ Account) each 6px radius, #2B2B2B background, #404040 border, 12px text

MAIN CONTENT — generate the HOME page:
A vertical stack with 20px gaps:

1. Hero Card (background #252525, 12px radius, 20px padding, drop-shadow 0 4px 20px rgba(0,0,0,.25)):
   - "Welcome to VEO Pipeline Pro" (24px/700 white)
   - "Professional AI Video Generation Suite" (13px #A0A0A0)
   - Two buttons row (12px gap): "▶ Start Generating" (orange #FF6B35, 600 weight, 10px×24px padding, 8px radius) + "📖 Documentation" (default #3A3A3A bg, white text, 8px radius)

2. Stats grid — 4 equal cards in single row (16px gap), each card same style (#252525, 12px radius, 20px padding, shadow):
   - "0" in 28px/700 #0078D4 + "Videos Today" in 12px #A0A0A0
   - "0" in 28px/700 #10B981 + "This Month"
   - "—" in 28px/700 #F59E0B + "Credits Left"
   - "0" in 28px/700 #FF6B35 + "Queue"

3. Quick Actions Card with title "Quick Actions" (14px/600) + subtitle "Most-used pipelines" (12px/#A0A0A0), then a row of 4 default buttons (48px height, equal flex): Text → Video, Image → Video, Idea → Video, Character Sync.

TYPOGRAPHY: Segoe UI Variable (or Inter as fallback). All UI weights are 400/500/600/700.

COLORS strictly:
- Primary blue: #0078D4 (hover #1A86D9, pressed #005A9E)
- Accent orange: #FF6B35 (only for create/run CTA)
- Success #10B981, Warning #F59E0B, Error #EF4444
- Surfaces: #1F1F1F (bg), #252525 (cards), #2B2B2B (sidebar/topbar/headers), #3A3A3A (inputs/buttons), #404040 (borders)
- Text: #FFFFFF (primary), #A0A0A0 (secondary), #707070 (muted)

NO gradients (except splash). NO light mode. NO pastel colors. NO icon-only navigation. NO hero gradients on content. Every card has a title. One CTA per primary action. Vietnamese copy preserved for user-facing labels but English for technical terms (Generate, API, Token, License).

Output: Tailwind CSS + React component. Make it pixel-precise and feel like a real Windows desktop app, not a marketing landing page.
```

---

## 📄 Per-page prompts (when generating other screens)

### Text → Video page

```
Reusing the VEO Pipeline Pro design system (sidebar 240px, topbar 56px, dark Fluent theme), generate the "Text → Video" page.

Top bar: title "Text → Video", subtitle "Generate Veo3 video from text prompt".

Content (28px padding, 16px gap stack):

1. Card "Prompt" with subtitle "Describe the video you want to generate":
   - Multi-line textarea (120px min height), placeholder "e.g. a young female English teacher saying 'Hello' clearly in classroom, photorealistic 9:16"
   - Background #3A3A3A, 8px radius, 1px #404040 border, focus border #0078D4

2. Card "Settings":
   - Single row, 4 columns (16px gap), each column has label above (12px/500 #A0A0A0, 4px gap) then a select/spin (36px height, #3A3A3A bg, 8px radius):
     • Model: ["Veo 3.1 Quality", "Veo 3.1 Fast", "Veo 3.1 Lite"]
     • Aspect: ["9:16 (Vertical)", "16:9 (Horizontal)", "1:1 (Square)"]
     • Duration: ["8 seconds", "6 seconds", "4 seconds"]
     • Count: SpinBox 1-4 default 1

3. Right-aligned action row: orange "▶ Generate Video" button (#FF6B35, 600 weight, 44px height, 200px min-width, 8px radius)

No grid, no decorative imagery. Pure form layout.
```

### Queue page

```
Reusing the design system, generate the "Queue" page.

Top bar: "Queue" / "Active generation jobs".

Content:

1. Stats row — 4 cards in row, same as Home stats but different metrics:
   - Active (#0078D4) | Queued (#F59E0B) | Completed Today (#10B981) | Failed Today (#EF4444)
   - Each shows large number (24px/700) + small label (11px #A0A0A0)

2. Card "Active Jobs":
   - Action row: "⏸ Pause All", "🗑 Clear Failed" left, "🔄 Refresh" right
   - Table (300px min height) with columns: # | Type | Prompt | Model | Progress | Status
   - Header background #2B2B2B, header text 12px/600 #A0A0A0
   - Rows alternate are NOT styled (single row color #252525)
   - Progress column shows 8px progress bar (#3A3A3A track, #0078D4 fill)
   - Status uses pill badges: Active=blue, Pending=warning, Completed=success, Failed=error

3. (empty state) — if no jobs, center "No active jobs" text in 13px #A0A0A0 with rose icon 🌹 above
```

### Settings page

```
Reusing design system, generate "Settings" page with 3 stacked cards:

1. Card "Account & License" with subtitle "Connected Google Flow account":
   - Single row: green dot pill "● Active" + text "user@example.com · ULTRA tier · 23,205 credits" + spacer + 2 default buttons "Re-login" "Add Account"

2. Card "Output" with subtitle "Where generated videos are saved":
   - 2 input rows, each: label above + text field + "Browse..." button right
   - Fields: "Video output dir", "Image output dir"

3. Card "Integrations" with subtitle "Drive sync + Telegram + Auto-update":
   - Form layout (label-left/field-right, 10px row gap):
     • Drive Folder ID
     • Drive Service Account JSON
     • Telegram Bot Token
     • Telegram Chat ID
     • Checkbox "Enable auto-update from GitHub every 6h" (checked default)

Bottom right: "Reset Defaults" (default) + "Save Settings" (primary blue #0078D4 button).
```

### License Activation Dialog

```
Generate a 680×420 modal dialog "VEO Pipeline Pro — Activate":

- Background #1F1F1F, 32px padding all sides, 16px section gap
- Title "Activate VEO Pipeline Pro" (22px/700 white)
- Subtitle "Enter your license key to unlock all features" (12px #A0A0A0)
- Field label "Machine ID" (11px/500 #A0A0A0) + read-only field showing "36F9EF779405DB3F36CA40B4" (monospace Cascadia Mono, color #0078D4)
- Field label "License Key" + input with placeholder "XXXX-XXXX-XXXX-XXXX"
- Bottom button row:
  - Left: "📋 Copy Machine ID" + "💬 Contact Truong Hoa" (default style)
  - Right: "✓ Activate" (primary blue #0078D4, 600, min-width 140, min-height 40)
- Footer link centered: "Get a license — Zalo 0345431884" (11px primary blue underlined)
```

### Bulk Login Dialog

```
Generate a 900×640 modal dialog "Bulk Auto-Login VEO3":

- Title "Bulk Auto-Login" (18px/700) + subtitle "Import .txt file (one line per account, format: email|password)" (11px #A0A0A0)
- File picker row: "📂 Choose accounts file (.txt)" + "📋 Paste from clipboard" buttons + spacer + "0 accounts loaded" label right
- Accounts table (max 220px height): columns "# | Email | Profile | Status", header bg #2B2B2B, status column shows "⏳ Pending" / "⚡ Running..." / "✅ Success" / "❌ <error>"
- Progress bar (8px height, #3A3A3A track, #0078D4 fill)
- Log textarea (min 200px height, monospace 11px, background #0F0F0F, color #DCDCDC, 6px radius, 1px #404040 border)
- Bottom buttons: "▶ Start Login All" (primary), "⏹ Stop" (default, disabled until running), spacer, "Close" (default)
```

---

## 🎨 Splash Screen

```
Generate a 640×360 launch splash screen for VEO Pipeline Pro:

- Diagonal linear gradient (135deg) from #0078D4 (top-left) → #1F1F1F (middle 50%) → #FF6B35 (bottom-right)
- Black overlay rgba(0,0,0,0.7) on top of gradient
- Left-aligned content with 40px left padding:
  - "VEO Pipeline Pro" (32px/700 white, Segoe UI)
  - "Professional AI Video Generation Suite" (12px #A0A0A0)
  - 3px solid #0078D4 horizontal line, 160px wide, below subtitle
  - Bottom-left: "v5.0.3 · Commercial · Truong Hoa" (10px #707070)
  - Bottom-right: "Loading..." (10px #A0A0A0)

Frameless window (no title bar, no chrome).
```

---

## ✅ Tips for using these prompts

1. **Upload `DESIGN.md` first** in Stitch (Settings or context tab) — gives full design tokens.
2. Use **Master Prompt** for Home page or first generation.
3. Use **Per-page prompts** for additional screens — they reference the design system without re-defining.
4. Stitch outputs Tailwind + React. Map Tailwind values:
   - `bg-[#1F1F1F]` for surfaces
   - `text-[#FFFFFF]` for primary text
   - `border-[#404040]` for hairlines
   - Custom colors via `tailwind.config.js` extension
5. Preview generated UI on **desktop frame** (not mobile) since this is a 1440×880 Windows app.

---

## 🚀 Quick copy-paste for Stitch input box

> Build a Microsoft Fluent dark-themed Windows desktop UI for "VEO Pipeline Pro" v5.0.3 Commercial. Persistent 240px sidebar (#2B2B2B) with brand header + 10 nav items + author footer (Truong Hoa, Zalo 0345431884), 56px top bar (#1F1F1F) with page title + 4 right action buttons, content area #1F1F1F with 28px padding. Cards have #252525 background, 12px radius, 20px padding, drop-shadow 0 4px 20px rgba(0,0,0,.25). Primary blue #0078D4 for nav active and Save buttons. Accent orange #FF6B35 ONLY for Generate/Run CTAs. Success #10B981, Warning #F59E0B, Error #EF4444 for status pills (15% transparent fill + 1px border). Inputs #3A3A3A bg with 8px radius, focus #0078D4 border. Typography Segoe UI Variable / Inter, 4 sizes max per screen (18 page title, 14 card title, 13 body, 12 label). NO light mode, NO gradients except splash, NO icon-only nav. Vietnamese-first UI copy, English technical labels. Generate the Home page with hero card (24px title + tagline + 2 CTAs), 4-column stats row (Videos Today / This Month / Credits Left / Queue), and Quick Actions card with 4 buttons.
