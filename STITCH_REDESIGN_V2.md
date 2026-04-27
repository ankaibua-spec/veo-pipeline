# Stitch Redesign Brief V2 — VEO Pipeline Pro

> Pass v1 đã có Sidebar + 7 pages cơ bản. Pass v2 này yêu cầu **upgrade đến chất lượng commercial** — nhìn như Linear / Raycast / Spotify desktop / Notion.

**Author:** Truong Hoa · Zalo `0345431884`
**Current version:** v5.1.5 PyQt6 + v5.2.0 Tauri scaffold

---

## ⚠ Current UI pain points (must fix)

1. **Inconsistency** — top section tab dùng theme dark Fluent, nhưng nội dung tab cũ (legacy PyQt) còn light blue (#d7e5ff) vá tạm bằng QSS override → trông patchwork
2. **Buttons mixed sizes** — Generate / Stop / View ở bottom row to thô, không hierarchy
3. **Forms cramped** — 8 input fields trong 1 cột không spacing đủ, label chen sát input
4. **Status panel** — table render thô, không có thumbnail preview, progress bar mờ
5. **Empty states** — chỉ text "Loading..." không có icon, không có guidance
6. **Dialog sizes** — License/Onboarding/Bulk Login/Drive Settings — mỗi cái 1 size khác, inconsistent padding
7. **Iconography** — đang dùng emoji 📁🔄⚙ → nên thay Lucide / Heroicons cho profesh hơn
8. **No motion** — switch tab cứng, không có transitions

---

## 🎯 Target aesthetic

**Linear.app meets Spotify desktop** — vibe:
- Dark with deep blacks (#0A0A0A → #1A1A1A) not just gray
- Subtle color accents (electric blue #4F8EF7, lime green #22D26B for success)
- High typographic contrast (Inter Display heavier weights)
- Generous whitespace — 32-48px page padding
- Smooth micro-interactions — 200ms ease everywhere
- Thumbnail-rich (every list item has preview / status pill / metadata stack)
- Keyboard-first — `Cmd+K` search, `?` shortcuts overlay

**NOT** like:
- Bootstrap admin templates
- SaaS dashboards (Salesforce / SAP)
- Material Design (too rounded, too playful)

---

## 📐 Updated design tokens

### Colors (refined)

| Token | v1 | v2 |
|-------|-----|-----|
| `--bg-primary` | `#1F1F1F` | `#0A0A0A` (deeper black) |
| `--bg-elevated` | `#252525` | `#141414` (cards) |
| `--bg-overlay` | `#2B2B2B` | `#1A1A1A` (sidebar, top bar) |
| `--bg-input` | `#3A3A3A` | `#202020` (inputs lighter than bg) |
| `--border` | `#404040` | `#2A2A2A` (subtler hairlines) |
| `--text-primary` | `#FFFFFF` | `#FAFAFA` (slightly off-white, easier on eyes) |
| `--text-secondary` | `#A0A0A0` | `#9CA3AF` (cooler gray) |
| `--text-muted` | `#707070` | `#6B7280` |
| `--accent-blue` | `#0078D4` (Microsoft) | `#4F8EF7` (electric, less corporate) |
| `--accent-violet` | — | `#A78BFA` (NEW — secondary actions) |
| `--accent-orange` | `#FF6B35` | `#FF7A45` (slightly softer) |
| `--success` | `#10B981` | `#22D26B` (more vibrant) |
| `--warning` | `#F59E0B` | `#FBBF24` (warmer) |
| `--error` | `#EF4444` | `#F87171` (less red, more pink-red) |

### Typography

```css
--font-display: "Inter Display", "Inter", system-ui;  /* tighter letter-spacing */
--font-body:    "Inter", system-ui;
--font-mono:    "JetBrains Mono", "Cascadia Code", monospace;
```

| Class | Size | Weight | Line | Use |
|-------|------|--------|------|-----|
| `.t-display` | 32px | 700 | 1.1 | Hero title only |
| `.t-h1` | 24px | 700 | 1.2 | Page title |
| `.t-h2` | 18px | 600 | 1.3 | Section header |
| `.t-h3` | 14px | 600 | 1.4 | Card title |
| `.t-body` | 14px | 400 | 1.5 | Default |
| `.t-small` | 12px | 400 | 1.4 | Labels |
| `.t-caption` | 11px | 500 | 1.3 | Hints, badges |

### Spacing (8pt grid, expanded)

| Token | px |
|-------|-----|
| `space-0` | 0 |
| `space-1` | 4 |
| `space-2` | 8 |
| `space-3` | 12 |
| `space-4` | 16 |
| `space-6` | 24 |
| `space-8` | 32 |
| `space-12` | 48 |
| `space-16` | 64 |

**Page padding-X: 48px** (was 28px). Cards spacing: 24px.

### Radius

| Token | px |
|-------|-----|
| `radius-sm` | 4 (pills) |
| `radius-md` | 8 (buttons, inputs) |
| `radius-lg` | 12 (cards default) |
| `radius-xl` | 16 (modals, hero cards) |
| `radius-pill` | 999 (status pills) |

### Elevation

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
--shadow-md: 0 4px 8px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.04);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.06);
--shadow-glow-blue: 0 0 0 3px rgba(79,142,247,0.2);
```

---

## 🎨 Component upgrades

### 1. Sidebar v2

```
┌────────────────────────────┐
│ ◆ VEO Pipeline Pro         │  brand mark + 24px name
│   v5.1.5 · Pro             │  caption
│                            │
│ ─────────────────          │
│                            │
│ ⌂  Home              ⌘1   │  shortcut hint right
│ ▷  Generate          ⌘2   │
│ 📦 Queue             3    │  ← live counter badge
│ ⏱  History                │
│ 👥 Accounts (3)           │  ← live counter
│ ☁  Drive             ✓    │  ← status indicator
│ ⚙  Settings              │
│                            │
│ ─────────────────          │
│                            │
│ 🟢 System OK              │  ← status pill
│                            │
│ Truong Hoa                 │  avatar 24px circle + name
│ Zalo 0345431884            │
└────────────────────────────┘
```

- 256px wide (was 240)
- Brand mark icon 24px next to name
- Each nav item shows keyboard shortcut on right (⌘1-9)
- Live counters as small pills (Queue, Accounts)
- Drive shows `✓` if connected, `–` if not
- System status pill at bottom (green = OK, yellow = warning, red = error)

### 2. Top bar v2

```
┌────────────────────────────────────────────────────────────────────────┐
│ Generate / Text → Video                          ⌘K   🔔 3   👤 P     │
│ ────────────────                                                        │
│ Queue: 2 active · 12 pending · 89% credits                             │
└────────────────────────────────────────────────────────────────────────┘
```

- 64px height (was 56)
- Page title 18px/600 + breadcrumb (Section / Page)
- Mini stats line below (live)
- Right cluster: Cmd+K search trigger · notification bell with unread badge · profile menu

### 3. Generate page (Text → Video) — biggest UI win

**Layout: 2-column (60/40 split):**

```
┌─────────────────────────────────────┬───────────────────────────────┐
│ Prompt (large textarea)              │  Settings panel              │
│                                      │                              │
│ [animated placeholder cycles examples]│  Model: ▼ Veo 3.1 Quality   │
│                                      │  Aspect: [9:16 ▎16:9 ▎1:1]   │
│                                      │  Duration: [4s 6s 8s]         │
│                                      │  Count: [— 2 +]               │
│                                      │                              │
│ ✨ Quick prompts (chips):            │  Cost: 100 tín dụng / video  │
│ [pronunciation] [advice] [tutorial]   │                              │
│                                      │  ────────────                │
│                                      │  ▶ Generate Video             │
│ 📎 Attach reference image             │     (large, full width)       │
│                                      │                              │
└─────────────────────────────────────┴───────────────────────────────┘
```

- Left: prompt textarea fills 60%, 200px min height, monospace optional toggle
- Animated placeholder text cycles through example prompts every 3s
- Quick prompt chips (clickable to insert)
- Right: settings stack with proper field labels
- Aspect/Duration/Count = segmented control NOT dropdown
- Generate button = large, primary, full width of right panel

### 4. Queue / History — list with thumbnails

Each row:
```
┌──────────────────────────────────────────────────────────────┐
│ [80×140 thumb] Title (16/600)                    [Status]   │
│                Topic · 1m 23s · Veo 3.1 Quality              │
│                ──── 85% ────────────                          │
│                Started 2:34 PM · ETA 30s     ⋮ menu          │
└──────────────────────────────────────────────────────────────┘
```

- 80×140 video thumbnail (9:16 ratio)
- Status pill top-right (Generating / Uploaded / Failed)
- Progress bar in row, animated
- Right kebab menu: Retry / Cancel / Open / Copy URL

### 5. Bulk Login dialog v2

Currently: text-heavy, table thin.

Upgrade:
- Full-screen dialog (1200×800)
- Left side: file drop zone (drag .txt OR paste textarea)
- Right side: parsed accounts as cards (not table)
- Each card shows email + status indicator (Pending / Running with spinner / ✓ Success)
- Bottom: progress bar + ETA "5/12 · ~3 min remaining"
- Live log expandable at bottom (collapsed by default)

### 6. Drive Settings v2

Currently: form fields stack.

Upgrade:
- Hero with status: big icon + "Connected to Google Drive" or "Not connected"
- If connected: shows email + folder name + last sync time
- 3 quick actions as cards (not buttons): Import from app.trbm.shop / Connect new account / Manual JSON
- Settings collapsed by default

### 7. License dialog v2

Currently: 680×420 boxy.

Upgrade:
- Centered card 480×560 (taller, narrower)
- Top: large lock icon + "Activate VEO Pipeline Pro" headline
- Machine ID block with copy button (always visible)
- Single license input field (large, monospace)
- 2 actions stacked: "Activate" (primary, full width) + "Buy a license — Zalo 0345431884" (link below)

---

## 🎬 Motion & micro-interactions

Add EVERYWHERE:
- Page transitions: 200ms `cubic-bezier(0.4, 0, 0.2, 1)` opacity + 8px Y translate
- Button hover: 120ms background-color
- Card hover: subtle lift via shadow-lg + 1px border highlight
- Modal enter: 250ms scale 0.96 → 1 + opacity
- Toast: slide-in top-right + auto-dismiss 4s
- Status pill pulse: green/red/yellow 2s gentle pulse for live state
- Loading: skeleton shimmer (gradient sweep), NOT spinner

---

## 📝 Final Stitch prompt (use this on stitch.withgoogle.com)

```
Generate VEO Pipeline Pro v2 — a premium dark-themed Windows desktop UI for AI video generation. Aesthetic target: Linear.app + Spotify desktop. Modern, deliberate, professional.

LAYOUT:
- 256px persistent sidebar (#1A1A1A bg, no border, just darkness contrast)
- 64px top bar (#0A0A0A bg, border-bottom 1px #2A2A2A)
- Content area #0A0A0A bg, 48px horizontal padding, 32px vertical
- All cards use #141414 bg with 12px radius, 24px padding, shadow 0 4px 8px rgba(0,0,0,0.3) + 1px inner border rgba(255,255,255,0.04)

SIDEBAR contains:
1. Brand at top: 24px diamond/spark icon next to "VEO Pipeline Pro" 18px/700 + caption "v5.1.5 · Pro" 11px #6B7280, 32px top padding
2. 1px divider #2A2A2A
3. Nav items 40px height with: 18px Lucide icon + 14px label + right-aligned 11px keyboard shortcut (⌘1, ⌘2...). Active = bg #4F8EF7/20 + 2px left border #4F8EF7. Hover = bg #1F1F1F. Text 600 weight when active.
4. Live counters as 18px-tall pill badges next to nav label (Queue: "3", Accounts: "3"). Drive shows "✓" when connected.
5. 1px divider before footer
6. System status pill (full width): green dot + "System OK" / yellow + "Drive sync paused" / red + "Login required"
7. User block: 24px circle avatar with letter "P" (Truong Hoa initial) + name + "Zalo 0345431884" link

TOP BAR:
- Left: Page title 18px/600 + 11px breadcrumb "Section / Subsection" above
- Below title: live stats line "Queue: 2 active · 12 pending · 89% credits" 12px #9CA3AF
- Right: Cmd+K search button (40×32 with kbd hint), bell with unread badge, 28px circle avatar dropdown

GENERATE PAGE (main feature, 2-column 60/40 split):
LEFT (60%):
- Card "Prompt" with subtitle "Describe what you want to create"
- Textarea 220px min-height, monospace toggle, animated placeholder cycling 3 example prompts
- Below textarea: row of quick-prompt chips (radius pill, #1F1F1F bg, hover #2A2A2A): "[Pronunciation lesson]" "[English advice]" "[Tutorial]" "[Storytelling]"
- Card below: "Reference image (optional)" with drop zone
RIGHT (40%):
- Card "Settings"
- Field "Model" — segmented control 3 options: Lite / Fast / Quality (Quality selected with #4F8EF7 bg)
- Field "Aspect ratio" — segmented control 9:16 / 16:9 / 1:1 with thumbnail icons
- Field "Duration" — segmented 4s / 6s / 8s
- Field "Count" — number stepper [- 2 +]
- Cost summary block: "100 tín dụng × 2 = 200 tín dụng" muted text
- Big primary button "▶ Generate Video" full width, 48px tall, #4F8EF7 bg, hover scale 1.02

QUEUE PAGE:
- Stats row: 4 small cards with icon + number + label (Active, Queued, Done Today, Failed Today)
- Filter chips: All / Generating / Done / Failed
- Row list, each row 100px tall:
  - Left: 80×140 video thumbnail (9:16, fallback dark gray with film icon)
  - Middle: Title 14px/600, metadata "Topic · 1m 23s · Veo 3.1 Quality" 12px #9CA3AF, animated progress bar 4px tall
  - Right: status pill (Generating yellow with spinner, Uploaded green, Failed red), kebab menu

COLORS strict:
- bg #0A0A0A (page) / #141414 (cards) / #1A1A1A (sidebar/topbar) / #202020 (inputs)
- borders #2A2A2A
- text #FAFAFA (primary) / #9CA3AF (secondary) / #6B7280 (muted)
- accent blue #4F8EF7 (primary) / orange #FF7A45 (Generate) / violet #A78BFA (secondary)
- success green #22D26B / warning #FBBF24 / error #F87171

TYPOGRAPHY: Inter Display for headings (700), Inter for body (400/600), JetBrains Mono for code/IDs.

MOTION:
- All hover transitions 120ms ease-out
- Page transitions 200ms cubic-bezier(0.4, 0, 0.2, 1) opacity + 8px Y
- Modal enter 250ms scale 0.96→1
- Status pill pulse 2s gentle for live state
- Skeleton shimmer for loading (NO spinner)

NO emojis in chrome — use Lucide icons everywhere. Keep emojis only in user content (chips, button labels for Vietnamese friendliness).

Output: full Vite + React 19 + Tailwind v4 + Motion + Lucide. Production-ready.
```

---

## 📦 Deliverable for Stitch

Copy block above into stitch.withgoogle.com. Upload these as context:
1. This file (`STITCH_REDESIGN_V2.md`)
2. Original `DESIGN.md` (v1 spec)
3. Screenshots of current UI bị xấu — particularly Settings tab, Bulk Login, Generate row

Stitch should output upgraded React app. Replace `tauri/src/` with new components.

---

**Author note:** Sau khi Stitch ra v2, em port vào `veo-ai-studio` repo + Tauri shell. Ship as Tauri t6.0.0 release.
