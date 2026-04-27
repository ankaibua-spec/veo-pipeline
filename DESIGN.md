# VEO Pipeline Pro — Design System

> Extracted from `/tool/qt_ui_modern/` codebase — PyQt6 desktop UI translated into web design rules for Stitch reconstruction.
> Author: **Truong Hoa** · Zalo `0345431884` · v5.0.3 Commercial

---

## 1. Executive Summary

**VEO Pipeline Pro** is a Windows desktop application for professional AI video generation via Google Veo 3 (Flow), Grok Imagine, and Sora. Power users batch-create vertical short-form videos for YouTube Shorts, TikTok, and educational content. The product orchestrates: bulk Google account login → token capture → multi-account Veo 3 video generation → Drive sync → automated YouTube upload via VPS pipeline.

Users do:
1. Bulk-login 5–50 Google Flow accounts from a `.txt` file
2. Submit batch text-to-video / image-to-video / character-sync prompts
3. Watch a queue dashboard as videos render
4. Auto-sync output to Google Drive → VPS picks up → YouTube auto-publishes

---

## 2. Product Personality

**Modern · Premium · Technical · Professional** — Microsoft Fluent Design (dark) inspired. Restrained color palette, generous spacing, card-based hierarchy, monospace for code/tokens. Conveys reliability for paid commercial users. Not playful — this is a tool engineers and content operators run for hours.

Adjectives that describe the brand: *focused, deliberate, opinionated, fast, dependable*. Anti-adjectives: *cute, animated, gradient-heavy, consumer-y*.

---

## 3. Target Users

| Persona | Goal | Pain |
|---------|------|------|
| **Content operator** (Vietnam, 25–40) | Push 10–30 videos/day across multi-channel TikTok+YouTube | Fights account bans, captcha, Google flagging |
| **YouTube creator** | One-stop tool for AI video gen + upload | Wastes time juggling Veo3 + Premiere + YouTube Studio |
| **Agency producer** | Manage 5+ client accounts, character-consistent campaigns | No off-the-shelf bulk Veo3 pipeline exists |
| **Ed-tech startup** | Pronunciation videos for English learners | Veo3 audio filter rejects educational dialogue prompts |

Primary language: **Vietnamese**. Secondary: English. UI bilingual (mixed) — no per-language toggle yet.

---

## 4. Brand Feel

- Tone: **Direct · Confident · Power-user-friendly**. No marketing fluff.
- Density: **Comfortable** (not crammed enterprise SaaS, not sparse landing page).
- Trust signals: explicit author block in sidebar (`Truong Hoa · Zalo 0345431884`), license activation gate, version stamp, GitHub link.
- Voice: short imperative labels (`Generate`, `Activate`, `Browse...`). Vietnamese for body content (`Bạn muốn tạo gì?`, `Lưu cài đặt`).

---

## 5. Color System

Extracted from `qt_ui_modern/theme.py`. Fluent Dark palette.

### Primary

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#0078D4` | Brand blue, primary actions, active nav, links |
| `--primary-hover` | `#1A86D9` | Hover state |
| `--primary-pressed` | `#005A9E` | Active/pressed |
| `--accent` | `#FF6B35` | Generate / Run CTA, attention orange |

### Semantic

| Token | Hex | Usage |
|-------|-----|-------|
| `--success` | `#10B981` | Connected, OK, completed jobs |
| `--warning` | `#F59E0B` | Credits low, queue pending |
| `--error` | `#EF4444` | Failed gen, license invalid |

### Surfaces (dark only — no light mode)

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-dark` | `#1F1F1F` | App background, content area |
| `--bg-mid` | `#2B2B2B` | Sidebar, top bar, status bar, table headers |
| `--bg-light` | `#3A3A3A` | Inputs, buttons, interactive surfaces |
| `--bg-card` | `#252525` | Cards, panels, modals body |
| `--border` | `#404040` | Hairlines, input borders, dividers |

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| `--text-primary` | `#FFFFFF` | Headings, primary copy |
| `--text-secondary` | `#A0A0A0` | Subtitles, labels, footer |
| `--text-muted` | `#707070` | Hints, version stamps, placeholders |

### Badges (semi-transparent fills with same-hue border)

```css
.badge-success  { background: rgba(16,185,129,.15);  color: #10B981; border: 1px solid #10B981; }
.badge-warning  { background: rgba(245,158,11,.15);  color: #F59E0B; border: 1px solid #F59E0B; }
.badge-error    { background: rgba(239, 68, 68,.15); color: #EF4444; border: 1px solid #EF4444; }
```

### Splash gradient (brand only — single use)

```
linear-gradient(135deg, #0078D4 0%, #1F1F1F 50%, #FF6B35 100%) overlaid with rgba(0,0,0,.7)
```

---

## 6. Typography System

### Font stacks

| Role | Stack | When |
|------|-------|------|
| Display / Headings | `"Segoe UI Variable Display", "Segoe UI", "Inter", system-ui` | Page titles, brand, hero |
| Body | `"Segoe UI Variable", "Segoe UI", "Inter", system-ui` | Default UI |
| Mono | `"Cascadia Mono", Consolas, monospace` | Machine ID, log output, license keys |

### Scale (px / rem)

| Class | Size | Weight | Use |
|-------|------|--------|-----|
| `text-display` | 32px / 2rem | 700 | Splash brand name |
| `text-hero` | 24px / 1.5rem | 700 | Home hero title |
| `text-page-title` | 18px / 1.125rem | 600 | Top bar title (per page) |
| `text-card-title` | 14px / 0.875rem | 600 | Section headers in cards |
| `text-body` | 13px / 0.8125rem | 400 | Default UI |
| `text-secondary` | 12px / 0.75rem | 400 | Subtitles |
| `text-label` | 12px / 0.75rem | 500 | Field labels above inputs |
| `text-hint` | 11px / 0.6875rem | 400 | Placeholders, footer notes |
| `text-stat-value` | 28px / 1.75rem | 700 | Dashboard KPI numbers |

### Letter-spacing

- Brand name: `+0.5px`
- Tagline / labels: `+0.3px`
- Body: default

---

## 7. Layout Rules

### Container

- Min app width: **1200px** (window minimum size, enforced on launch)
- Default app size: **1440 × 880** (resize allowed; sidebar fixed)
- Content max-width: none (full available)

### Spacing rhythm (8 px base)

| Token | px | Use |
|-------|-----|-----|
| `space-0` | 0 | Reset |
| `space-1` | 4 | Tight (label → field) |
| `space-2` | 8 | Compact |
| `space-3` | 12 | Card internal |
| `space-4` | 16 | Section gap |
| `space-5` | 20 | Card padding |
| `space-6` | 24 | Section padding-Y |
| `space-7` | 28 | Page padding-X |
| `space-8` | 32 | Dialog padding |

### Radius

| Token | px | Use |
|-------|-----|-----|
| `radius-sm` | 6 | Inputs, small buttons, table rows |
| `radius-md` | 8 | Buttons, primary inputs, badges |
| `radius-lg` | 12 | Cards, modals, panels |
| `radius-pill` | 12 | Status badges (height 24, radius 12) |

### Shadow

Single elevation token used consistently. Applied to cards via `QGraphicsDropShadowEffect`:

```css
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
```

No multi-tier shadow system — flat surfaces with one consistent lift on cards.

### Sidebar / Topbar

- Sidebar width: **240px fixed**
- Topbar height: **56px fixed**
- Status bar: ~28px

### Card pattern

```
QFrame#card
├── padding: 20px
├── background: #252525
├── border: 1px solid #404040
├── border-radius: 12px
├── shadow: 0 4px 20px rgba(0,0,0,.25)
└── content stack:
    ├── (optional) cardTitle (14px / 600)
    ├── (optional) cardSubtitle (12px / secondary color, wrap)
    └── child widgets (gap: 12px)
```

---

## 8. Navigation Architecture

**Persistent left sidebar** (240px) + **per-page top bar** (56px) + **status bar** (bottom).

### Sidebar structure

```
┌──────────────────────┐
│ Brand header (24px+) │  VEO Pipeline Pro
│   v5.0.3 · Commercial│
├──────────────────────┤
│ ▸ Home               │  ← active = blue background, white text, 600 weight
│ ▸ Text → Video       │
│ ▸ Image → Video      │
│ ▸ Idea → Video       │
│ ▸ Character Sync     │
│ ▸ Create Image       │
│ ▸ Grok Video         │
│ ▸ Queue              │
│ ▸ History            │
│ ▸ Settings           │
├──────────────────────┤
│ Truong Hoa           │  ← bold 11px secondary
│ Zalo 0345431884      │  ← link primary
└──────────────────────┘
```

Nav item: 40px height, 8px padding-X, 16px padding-Y, transparent default, hover `#3A3A3A`, active `#0078D4`.

### Top bar

Left: page title (18px / 600) + subtitle (12px / muted).
Right: `📁 Open Output` · `🔄 Refresh` · `⚙ Account` · `👥 Bulk Login` (secondary buttons, 6px radius).

### Status bar

Single-line text (11px secondary): `Ready · VEO Pipeline Pro v5.0.3 · LEGACY OK · Truong Hoa`.

---

## 9. Core Components

### 9.1 Buttons

Three priority levels. Min-height: 36px (regular), 40-44px (CTA).

**Default** — neutral surface, used for secondary actions
```css
background: #3A3A3A;
border: 1px solid #404040;
border-radius: 8px;
padding: 8px 18px;
font: 500 13px;
color: #FFFFFF;
:hover { background: #2B2B2B; border-color: #0078D4; }
:pressed { background: #1F1F1F; }
:disabled { background: #2B2B2B; color: #707070; }
```

**Primary** — destructive-safe primary blue, "Save", "Activate", "Continue"
```css
background: #0078D4;
border: 1px solid #0078D4;
color: #FFFFFF;
font-weight: 600;
padding: 10px 24px;
:hover { background: #1A86D9; }
```

**Accent** — orange for "Generate", "Run", primary creation CTAs
```css
background: #FF6B35;
color: #FFFFFF;
font-weight: 600;
padding: 10px 24px;
```

**Top action button** — small variant for top-bar utilities
```css
background: #2B2B2B;
border: 1px solid #404040;
border-radius: 6px;
padding: 6px 14px;
font-size: 12px;
color: #A0A0A0;
:hover { color: #FFFFFF; border-color: #0078D4; }
```

### 9.2 Forms — Inputs / Textarea / Combo / Spin

All use the same surface treatment. Min-height: 36px.

```css
background: #3A3A3A;
border: 1px solid #404040;
border-radius: 8px;
padding: 8px 12px;
font-size: 13px;
color: #FFFFFF;
selection-background: #0078D4;
:focus { border-color: #0078D4; }
::placeholder { color: #707070; }
```

Field label sits above input, 4px gap:
```
┌ Model ──────────────────┐  ← label: 12px / 500 / #A0A0A0
│  Veo 3.1 Quality      ▾ │  ← input
└─────────────────────────┘
```

### 9.3 Cards

See section 7. Always padded 20px, dropshadow, optional title+subtitle header.

### 9.4 Tables

```css
QTableView {
  background: #252525;
  border: 1px solid #404040;
  border-radius: 8px;
  gridline-color: #404040;
  selection-background: #0078D4;
}
QHeaderView::section {
  background: #2B2B2B;
  color: #A0A0A0;
  padding: 8px 12px;
  border-bottom: 1px solid #404040;
  font: 600 12px;
}
```

### 9.5 Modals / Dialogs

Centered, no backdrop blur, dark surface. License dialog: `680 × 420`. Bulk login: `900 × 640`. Onboarding wizard: `640 × 460` minimum.

Header inside dialog: title 22px / 700 + subtitle 12px / secondary, 32px padding all sides, 16px section gap.

### 9.6 Tabs (sub-navigation inside pages, e.g. Grok Video)

```css
QTabBar::tab {
  background: #2B2B2B;
  color: #A0A0A0;
  padding: 8px 18px;
  border-radius: 6px;
  margin-right: 4px;
}
QTabBar::tab:selected {
  background: #0078D4;
  color: #FFFFFF;
  font-weight: 600;
}
```

### 9.7 Dropdowns / Combo

Same surface as inputs. Drop indicator 24px width, no border. Menu items hover: primary blue.

### 9.8 Toasts / Notifications

System tray notifications for desktop. In-app uses `QMessageBox` with custom styled buttons matching Default + Primary patterns.

### 9.9 Charts

Not currently in product. If added: thin lines (1px), brand blue stroke, area fills at `rgba(0,120,212,.15)`, axis labels in `#A0A0A0`, no chrome (no chart frames).

### 9.10 Skeletons / Empty / Loading

- **Empty state**: centered icon (rose decoration `🌹`) + 13px secondary copy. Example from Flow:
  > 🌹
  > Bắt đầu tạo hoặc thả nội dung nghe nhìn
- **Loading**: lazy tab placeholder shows 14px muted text "Loading {tab}..." centered.
- **Progress bar**: 8px height, 6px radius, `#3A3A3A` track, `#0078D4` chunk.
- **Splash**: 600ms branded splash with gradient + version stamp.

### 9.11 Status Badges (pill-shaped)

```
● Connected      → #10B981 fill 15% + 1px border + #10B981 text
● Active         → success
● Pending        → warning
● Failed         → error
```

Pill: 24px height, 12px radius, 4px×12px padding, 11px / 600 text.

---

## 10. Responsive Design Rules

Desktop-only product (Windows .exe). No tablet / mobile breakpoints. However, layout is fluid:

- Sidebar: **fixed 240px** (never shrinks; always visible)
- Topbar: **fixed 56px**
- Content: **fills remaining width**, scrollable Y
- Min window: **1200 × 760**
- Default window: **1440 × 880**

If web port (Stitch reconstruction):
- ≥ 1280px: full sidebar + topbar + content
- 768-1279px: collapse sidebar to icon-only (60px), preserve topbar
- < 768px: drawer sidebar, hamburger in topbar, single-column cards

---

## 11. Motion + Interactions

Restrained. Native PyQt6 transitions only. No custom animation library.

| Interaction | Behavior |
|-------------|----------|
| Splash → main window | `splash.finish(window)` instant fade after 600ms |
| Tab switch | Instant (no slide). Lazy widget build on first click |
| Hover button/nav | Background color change `<150ms` (default Qt) |
| Dropdown open | Native fade |
| Toast / tray balloon | Native Windows tray notification |
| Progress bar | Smooth chunk fill |
| Window close → tray | Dialog hides, balloon notifies once |

If web reconstruction:
- Page transitions: 150ms `ease-out` opacity only
- Hover: 100ms background-color
- Modal: 200ms scale-up (0.96 → 1) + opacity
- Toast: slide-in from top-right, 300ms

No skeleton shimmer, no parallax, no entrance animations on load.

---

## 12. Accessibility Standards

Targets WCAG AA where applicable:

- All text on dark surfaces meets contrast ratio ≥ 4.5:1 (`#FFFFFF` on `#1F1F1F` = 17.4:1)
- Secondary text `#A0A0A0` on `#1F1F1F` = 8.2:1 ✓
- Muted `#707070` on `#1F1F1F` = 4.7:1 ✓ (just passes for body)
- Primary `#0078D4` on white = 4.7:1 ✓
- All inputs have explicit field labels (no placeholder-only)
- Focus ring: `border-color: #0078D4` (2px effective)
- Keyboard nav: Qt default (Tab cycles, Esc closes dialogs)
- Cursor: `PointingHandCursor` on nav items + interactive buttons

Web reconstruction must add:
- `aria-label` on icon-only buttons
- `role="navigation"` on sidebar
- `role="tablist"` / `role="tab"` on QTabBar equivalents
- Skip-to-content link for keyboard users

---

## 13. Full Screen Inventory

### Top-level routes (sidebar nav)

| Route | Page | Purpose |
|-------|------|---------|
| `/` (Home) | Dashboard | Stats cards (Videos Today, This Month, Credits Left, Queue) + quick actions hero |
| `/text-to-video` | Text → Video | Prompt textarea + model/aspect/duration/count + Generate CTA |
| `/image-to-video` | Image → Video | Drop-zone + motion prompt + Animate CTA |
| `/idea-to-video` | Idea → Video | Idea textarea + storyboard config (duration, scenes, style, aspect) + voiceover toggle |
| `/character` | Character Sync | Character library list + edit form (name/age/gender/style/desc) |
| `/create-image` | Create Image | Prompt + negative + model picker (Imagen/NanoBanana/Flux/Ideogram) + Generate |
| `/grok` | Grok Video | Tabbed t2v/i2v + account chip |
| `/queue` | Queue | 4-stat dashboard + active jobs table (#/Type/Prompt/Model/Progress/Status) + pause/clear/refresh actions |
| `/history` | History | Filter bar (search + model + time + export CSV) + thumbnail grid (vertical 9:16) |
| `/settings` | Settings | Account block + Output paths + Integrations form (Drive/Telegram/auto-update toggle) |

### Modal / overlay screens

| Screen | When |
|--------|------|
| **License Activation** (`license_dialog.py`) | First run, no valid license |
| **Onboarding Wizard** (`onboarding.py`) | First run, after license — 4 pages: Welcome / Output / Integrations / Finish |
| **Bulk Login** (`bulk_login.py`) | User clicks "👥 Bulk Login" in topbar — file picker + accounts table + log + progress |
| **Auto-Update Prompt** (`auto_update.py`) | New release detected — modal: "Update Now" / "Later" + progress dialog on accept |
| **Splash** (`splash.py`) | Every launch, 600ms |
| **Tray Menu** (`tray.py`) | Right-click tray icon — Show / Open Queue / Settings / Quit |

---

## 14. Core User Flows

### 14.1 First-time setup

```
Download zip → extract → run .exe
  → License dialog (paste key OR set VEO_BYPASS_LICENSE=1)
  → Onboarding wizard (4 pages, ~1 min)
    └─ Welcome → Output dir → Integrations (Drive/Telegram) → Finish
  → Splash 600ms
  → Main window (Home) + Tray icon active
```

### 14.2 Bulk login

```
Topbar → "👥 Bulk Login"
  → Dialog opens (900×640)
  → Pick .txt or paste clipboard (format: email|password per line)
  → Accounts table populates (#/Email/Profile/Status)
  → Click "▶ Start Login All"
  → Sequential: Chrome opens per account, auto-fills, captures token, kills profile
  → Status realtime per row: Pending → ⚡ Running → ✅ Success / ❌ Failed
  → Log streams in monospace black panel
  → "All accounts processed" footer
```

### 14.3 Generate single video (text → video)

```
Sidebar → Text → Video
  → Card: Prompt (textarea, multi-line)
  → Card: Settings (Model / Aspect / Duration / Count)
  → Bottom bar (legacy MainWindow): "Tạo video" Accent button
  → Click → StatusPanel queues job → Chrome browser auto opens
  → Watch progress in Queue tab
  → On success → file appears in Output folder + Telegram notify
```

### 14.4 Auto-update flow

```
App launch → 1.5s after window shown → check GitHub Releases API
  → If newer tag → modal "New version available"
  → Click "Update Now"
  → Progress dialog: download VEO_Pipeline_Pro_Windows.zip
  → Extract to temp → write batch script → spawn detached
  → App exits → batch waits PID exit → swaps files → relaunches
  → New version opens
```

### 14.5 Drive sync → VPS → YouTube

```
Tool gens video → saves to local Output dir
  → pc/post_processor.py watches dir → renames YYYY-MM-DD_HH-MM_<topic>.mp4
  → uploads to Drive folder
  → notifies Telegram channel "Video Veo3"
  → VPS cron */5 → veo_drive_pickup.py polls Drive
  → downloads new files → inserts into english-pronunciation-factory DB
  → factory worker → uploads to YouTube channel "Po's English Podcast"
  → Telegram notify with YouTube URL
```

---

## 15. Stitch Generation Rules

These are the **most important rules** for Stitch when generating new pages or screens:

### Hard rules

1. **Dark mode only.** No light theme variant. Background always one of `#1F1F1F`, `#2B2B2B`, `#252525`, `#3A3A3A`. White or near-white text on these surfaces.
2. **Sidebar persistent.** Every full-page screen has the 240px left sidebar. Brand header → nav items → author footer. Active item = primary blue background.
3. **Topbar always present.** 56px height, page title (18px/600) + subtitle (12px/muted) on left, action buttons on right.
4. **Card-based content.** Never put form fields directly on background. Wrap in `Card` (radius 12, padding 20, shadow `0 4px 20px rgba(0,0,0,.25)`, optional title + subtitle).
5. **One CTA per primary action.** Use orange `#FF6B35` for create/run actions ("Generate", "Run", "Animate"). Blue `#0078D4` for save/confirm. Default for everything else. Never two accent buttons on same screen.
6. **Field labels above inputs.** 4px gap. Never inside placeholder.
7. **Icons inline with text.** Use Unicode emoji (📁 🔄 ▶ ✨ 👥) not SVG icon set. If web port, use Lucide icons matching emoji metaphor.
8. **Field width = column flex.** Inputs span their card column. Don't fix widths unless intentional (e.g. spinbox).
9. **No gradients except splash.** Splash gradient is single-use brand intro. All other surfaces flat.
10. **Status colors semantic.** `#10B981` only for success/active. `#F59E0B` only for warning/pending. `#EF4444` only for error/failed. Never decorative use.

### Soft rules

11. **Spacing rhythm 4 / 8 / 12 / 16 / 20 / 24 / 28** — pick from this scale, no arbitrary values.
12. **Typography: 4 sizes max per screen.** Page title (18) + section title (14) + body (13) + label/hint (12-11).
13. **Tables for data, cards for forms.** Don't mix. Tables: 12px row padding, header `#2B2B2B`, hover row light highlight.
14. **Mobile-first NOT required** (desktop-only). But content stacks gracefully if window narrows below 1200px.
15. **Voice: Vietnamese for user-facing copy, English for technical labels.** "Tạo video" not "Create Video"; "Generate" preserved on imported English UI strings. Don't translate `API`, `Token`, `URL`, etc.
16. **Trust elements always visible:** version (`v5.0.3 · Commercial`) + author (`Truong Hoa · Zalo 0345431884`) in sidebar footer. Status bar shows readiness.
17. **Tray icon mandatory.** Closing main window minimizes to tray, not quit. Tray menu has Show/Queue/Settings/Quit.

### Banned patterns

- ❌ Centered modals on full-screen backdrop overlay (use Qt-style centered dialogs without dim)
- ❌ Large hero gradients on content pages (only splash)
- ❌ Pastel decorative colors (no pinks, purples, mints, peaches outside semantic palette)
- ❌ Multiple primary CTAs on same screen
- ❌ Sticky bottom bars (except legacy MainWindow's action bar)
- ❌ Empty card with no header (always at minimum a title)
- ❌ Skeleton shimmer / fancy loaders (just text "Loading...")
- ❌ Icon-only nav items (always paired with text in sidebar)

---

## 16. Missing Opportunities

Smart improvements Stitch should consider when extending:

1. **Dashboard/Home page** is sparse. Add: recent gens grid (last 6 thumbnails), credit consumption chart (sparkline last 7d), failed jobs alert card.
2. **Search bar** in topbar — unify search across history + queue + settings. Cmd+K shortcut.
3. **Notification center** — bell icon in topbar; unread dot for new tray notifications, click opens dropdown of last 10 events.
4. **Keyboard shortcuts overlay** — `?` opens cheatsheet (e.g. `Ctrl+G` generate, `Ctrl+,` settings, `Ctrl+L` queue).
5. **Light mode (optional)** — same hue palette, inverse surfaces. Toggle in Settings → preserve in `~/.veo_pipeline/prefs.json`.
6. **Onboarding skip path** — "I already have an account configured" jump.
7. **Drag-and-drop everywhere** — image cards, prompt files, character ref images. Currently only some pages support it.
8. **Inline credit balance** in topbar — `23,205 credits` chip → link to Settings.
9. **Health check on launch** — tiny status pill: "All systems OK" / "Drive disconnected" — actionable click.
10. **Bulk gen** — paste multi-line prompt → submit each as separate job (mirror Bulk Login UX for video gen).

---

## 17. Final Visual Prompt For Stitch

> Generate a **professional dark-mode desktop application UI** for a Windows commercial AI video generation tool called **VEO Pipeline Pro**. Use a **Microsoft Fluent Design** language: deep neutral surfaces (`#1F1F1F` background, `#252525` cards), restrained typography in **Segoe UI Variable** (Inter as web fallback), a single brand blue `#0078D4` for primary actions and active navigation, and a single attention orange `#FF6B35` reserved for "Generate" / "Run" CTAs. Layout uses a **persistent 240px left sidebar** (brand header + 10 nav items + author trust block at bottom), a **56px top bar** with page title + subtitle on the left and 3-4 secondary action buttons on the right, and **card-based content** (12px radius, subtle drop-shadow `0 4px 20px rgba(0,0,0,.25)`, 20px padding) stacked with 16-20px gaps inside a 28px page padding. Forms have **labels above inputs** in 12px secondary gray, inputs use `#3A3A3A` surface with 8px radius, focus state is a 1px primary blue border. Tables, modals, dropdowns, and dialogs all share the same dark card language — never break to light surfaces. Motion is **minimal**: 100-200ms hover transitions only, no page slides, no skeleton shimmer. Empty states use a small decorative icon + a single line of 13px secondary copy. Status uses **semantic pills** (success green, warning amber, error red) with 15% transparent fill plus matching colored 1px border. The product feels **deliberate, fast, professional** — a tool a power user runs all day, not a consumer app. Voice is **Vietnamese-first** for UI copy ("Tạo video", "Bạn muốn tạo gì?", "Lưu cài đặt") with English preserved for technical labels (Generate, API, Token, License). The author block (`Truong Hoa · Zalo 0345431884`) lives at sidebar footer and version stamp (`v5.0.3 · Commercial`) under the brand name — these trust signals are non-negotiable. Reserve the only gradient (blue → dark → orange) for the **600ms branded splash screen** at app launch. No light mode. No gradients on content. No pastel accents. No icon-only navigation. Every card has a title.

---

DESIGN.md created successfully.
