# Stitch Prompts — Copy & Paste

Mỗi block = 1 prompt, paste vào https://stitch.withgoogle.com input box, **iterate từng cái**.

Output: Tailwind v4 + React 19 + Lucide icons + Motion.

---

## 🌟 Master directive (paste vào "System / Context" của Stitch nếu có)

```
You are designing VEO Pipeline Pro — a premium commercial Windows desktop app for AI video generation. Author: Truong Hoa.

DESIGN LANGUAGE:
- Reference: Linear.app + Spotify desktop + Raycast
- Premium dark mode ONLY (no light theme variant)
- Deep blacks: bg #0A0A0A page, #141414 cards, #1A1A1A sidebar/topbar, #202020 inputs
- Borders: hairlines #2A2A2A
- Text: #FAFAFA primary, #9CA3AF secondary, #6B7280 muted
- Accents: #4F8EF7 electric blue (primary CTA, active nav), #FF7A45 orange (Generate/Run only), #A78BFA violet (secondary)
- Status: #22D26B success, #FBBF24 warning, #F87171 error (use 15% transparent fill + 30% border for pills)

TYPOGRAPHY:
- Headings: "Inter Display" 700 weight, tight letter-spacing -0.02em
- Body: "Inter" 400/600
- Mono: "JetBrains Mono" for IDs, code, license keys
- Sizes: 32 hero / 24 page-title / 18 section / 14 body+card-title / 12 label / 11 caption

LAYOUT TOKENS:
- Spacing 8pt grid: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64
- Radius: 4 pills / 8 buttons-inputs / 12 cards / 16 modals
- Shadow elevated: 0 4px 8px rgba(0,0,0,0.3) + inset 0 0 0 1px rgba(255,255,255,0.04)
- Page padding: 48px horizontal, 32px vertical

ICONS: Lucide React only — NO emojis in chrome (status pills, nav, buttons). Emojis OK only in user-content like quick-prompt chips.

MOTION:
- Hover transitions: 120ms ease-out background-color
- Page transitions: 200ms cubic-bezier(0.4, 0, 0.2, 1) opacity + 8px Y translate
- Modal enter: 250ms scale 0.96→1 + opacity
- Status pulse: 2s gentle for live state
- Loading: skeleton shimmer (gradient sweep), NEVER spinner

OUTPUT: Vite + React 19 + Tailwind v4 + Motion + Lucide. Production-ready, accessible (WCAG AA), keyboard-first.

NEVER:
- Emojis in chrome (use Lucide)
- Gradients on content (only splash screen)
- Border-radius > 16px (avoid bubbly)
- Multiple primary CTAs on same screen
- Light surfaces (no white bg anywhere)
```

---

## 1️⃣ Prompt: Sidebar (256px)

```
Generate the Sidebar component for VEO Pipeline Pro:

256px fixed width, bg #1A1A1A, full height, no border (rely on contrast against #0A0A0A content area).

CONTENT (top to bottom):
1. Brand block (32px top padding, 24px horizontal): 28×28 diamond/spark icon (Lucide "Sparkles") in gradient #4F8EF7→#A78BFA next to "VEO Pipeline Pro" 18px/700 letter-spacing -0.02em. Below in 11px #6B7280 caption: "v5.1.5 · Pro"
2. 1px divider #2A2A2A, 24px margin
3. Nav items list — each 40px tall, 12px horizontal padding, 8px gap between items:
   - Lucide icon 18px (left)
   - Label 14px/500 (Inter)
   - Right: keyboard shortcut "⌘1" through "⌘9" in 11px #6B7280 monospace
   - States: default text #9CA3AF · hover bg #1F1F1F text #FAFAFA · active bg rgba(79,142,247,0.15) + 2px left border #4F8EF7 + text #FAFAFA 600 weight
   - Items: Home (Home icon, ⌘1), Generate (Wand2, ⌘2), Queue (ListChecks, ⌘3) with green pill "3" badge for active count, History (History, ⌘4), Accounts (Users, ⌘5) with pill "12" badge, Drive (Cloud, ⌘6) with green check ✓ (Lucide CheckCircle2 small) when connected, Settings (Settings, ⌘9)
4. 1px divider before footer
5. System status pill (full-width, 32px tall): green dot 8px + "System OK" 12px/500 — animates 2s pulse
6. User block (24px padding): 28px circle avatar bg #4F8EF7 with letter "P" centered (Truong Hoa = P) + name "Truong Hoa" 13px/600 + "Zalo 0345431884" link 11px #4F8EF7

Stack with React + Tailwind. Use lucide-react. Add Motion fade-in on mount.
```

---

## 2️⃣ Prompt: Top Bar (64px)

```
Generate Top Bar for VEO Pipeline Pro:

64px height, bg #0A0A0A, border-bottom 1px #2A2A2A, padding 24px horizontal.

LEFT BLOCK (vertical stack 2px gap):
- Breadcrumb 11px #6B7280: "Generate / Text → Video"
- Page title 18px/700 letter-spacing -0.02em #FAFAFA: "Text → Video"
- Below title in 12px #9CA3AF: "Queue: 2 active · 12 pending · 89% credits"

RIGHT BLOCK (horizontal, 12px gap):
- Cmd+K search trigger: pill button 36px tall, 14px horizontal padding, bg #1A1A1A border 1px #2A2A2A radius 8px. Inside: Lucide Search icon 14px + text "Search" 13px #9CA3AF + spacer + kbd "⌘K" in 11px monospace #6B7280 inside small chip bg #2A2A2A
- Notification bell: 36×36 button bg transparent hover #1A1A1A radius 8px, Lucide Bell icon 18px #9CA3AF, with red dot #F87171 6px top-right when unread
- Avatar dropdown: 32px circle bg #4F8EF7 with "P" + Lucide ChevronDown 12px to the right

Sticky position. Subtle shadow when content scrolls under: 0 1px 0 #2A2A2A.

React + Tailwind + lucide-react.
```

---

## 3️⃣ Prompt: Generate Page (60/40 split)

```
Generate the "Text → Video" main page for VEO Pipeline Pro.

LAYOUT: 2-column grid, 60% left + 40% right, 24px gap. Page padding 48px.

LEFT COLUMN (60%):

Card "Prompt" (bg #141414, padding 24px, radius 12px, shadow 0 4px 8px rgba(0,0,0,0.3) + inset 0 0 0 1px rgba(255,255,255,0.04)):
- Header: 14px/600 "Prompt" + 12px #9CA3AF subtitle "Describe what you want to create"
- Textarea: bg #202020, border 1px #2A2A2A radius 8px, focus border #4F8EF7 + glow shadow 0 0 0 3px rgba(79,142,247,0.2). 220px min-height. Padding 16px. Font 14px Inter. Animated placeholder cycling every 3s through:
  • "a young female English teacher pronouncing the letter D, photorealistic 9:16"
  • "cinematic ocean sunset, slow zoom out, golden hour"
  • "a barista pouring latte art, close up macro shot"
- Below textarea: row of "Quick prompts" chips horizontally scrollable: pill bg #1F1F1F border #2A2A2A radius full, padding 6px 12px, hover bg #2A2A2A: "Pronunciation lesson" / "English advice" / "Tutorial" / "Storytelling" / "Product demo"
- Bottom row: Lucide Paperclip icon 14px + text "Attach reference image (optional)" 12px #9CA3AF link

RIGHT COLUMN (40%):

Card "Settings":
- Field "Model" with label 11px/500 uppercase tracking-wider #6B7280 above. Segmented control 3 options Lite / Fast / Quality — single bar bg #202020 radius 8px, each option flex-1 padding 8px center, selected bg #4F8EF7 text white shadow-sm
- Field "Aspect ratio": segmented control 9:16 / 16:9 / 1:1 with 16×16 preview rect icon next to each label
- Field "Duration": segmented 4s / 6s / 8s
- Field "Count": stepper [- 2 +] horizontal, minus/plus buttons 32×32 bg #202020 radius 6px

Then thin divider 1px #2A2A2A vertical 16px margin

- Cost summary block: small text 12px #9CA3AF "Cost: 100 credits × 2 = " + larger 14px/600 #FAFAFA "200 credits"

Card "Generate" (separate card below settings):
- Big primary button: 100% width, 52px tall, bg #FF7A45 text white 15px/600. Lucide Play icon 18px + "Generate Video". Hover scale 1.02 + brightness 1.1. Shadow #FF7A45 glow on hover.
- Below button: 11px #6B7280 "Estimated time ~ 90 seconds per video"

React + Tailwind. State for selected model/aspect/duration/count.
```

---

## 4️⃣ Prompt: Queue Page (rows with thumbnails)

```
Generate Queue page for VEO Pipeline Pro.

PAGE PADDING 48px horizontal, 32px vertical, 24px section gap.

TOP: 4 stat cards in equal grid (gap 16px), each card bg #141414 radius 12px padding 20px:
- Card 1: Lucide Loader2 icon 18px #4F8EF7 spinning + label 11px uppercase tracking-wider #6B7280 "ACTIVE" + number 28px/700 #FAFAFA "2"
- Card 2: Lucide Clock 18px #FBBF24 + "QUEUED" + "12"
- Card 3: Lucide CheckCircle2 18px #22D26B + "DONE TODAY" + "47"
- Card 4: Lucide XCircle 18px #F87171 + "FAILED TODAY" + "1"

FILTER BAR: pill toggle group horizontal, gap 8px, bg #141414 radius full padding 4px:
- "All (62)" / "Generating" / "Done" / "Failed" — active pill bg #4F8EF7 text white, inactive #9CA3AF hover bg #1F1F1F

JOB LIST: vertical stack of rows, each 100px tall card bg #141414 radius 12px padding 16px shadow elevated, 8px gap between rows:
- LEFT: 80×140 thumbnail (9:16 ratio) bg #1A1A1A radius 8px. If video done: actual thumbnail. If generating: placeholder with Lucide Film icon 32px #6B7280 centered. Optional play overlay on hover.
- MIDDLE flex column gap 6px:
  - Title 14px/600 #FAFAFA "How to Pronounce the letter D in English"
  - Metadata row 12px #9CA3AF: Lucide Hash icon "5" · "Pronunciation" · Lucide Clock "1m 23s" · "Veo 3.1 Quality"
  - Progress bar 4px tall bg #1F1F1F radius full, fill bg gradient #4F8EF7→#A78BFA animated stripe (only if generating). Shows percentage "85%" right-aligned 11px #9CA3AF
  - Started time 11px #6B7280: "Started 2:34 PM · ETA 30s"
- RIGHT vertical:
  - Status pill at top: yellow "Generating" with spinning Loader2 OR green "Done" with Check OR red "Failed" with X. Pill = 24px tall, radius full, bg 15% color, text 100% color, border 30% color.
  - Below pill: Kebab menu Lucide MoreVertical 18px button — dropdown with "Retry / Cancel / Open file / Copy URL"

Empty state: when no jobs, center the page with Lucide ListChecks 48px #2A2A2A icon + "No jobs in queue" 16px #9CA3AF + "Generated videos appear here" 12px #6B7280.

Use Motion for row entrance: stagger 50ms each, fade-in + 8px Y translate.

React + Tailwind + lucide-react + motion.
```

---

## 5️⃣ Prompt: Bulk Login Dialog (full-screen)

```
Generate Bulk Login dialog for VEO Pipeline Pro.

Modal overlay rgba(0,0,0,0.7) blur-md. Center 1200×800 dialog, bg #141414 radius 16px padding 32px shadow-2xl.

HEADER row:
- Left: Lucide Users icon 24px #4F8EF7 + title 18px/700 "Bulk Account Login" + subtitle 12px #9CA3AF "Login multiple Google Flow accounts in sequence"
- Right: close button Lucide X 20px hover bg #2A2A2A radius 6px

BODY 2-column 50/50 split, gap 24px:

LEFT panel (input):
- Drop zone full height min 400px, bg #1A1A1A border 2px dashed #2A2A2A radius 12px center content. Hover/drag: border-color #4F8EF7 bg rgba(79,142,247,0.05). Inside:
  - Lucide Upload icon 48px #4F8EF7
  - Title 16px/600 "Drop accounts file here"
  - Subtitle 12px #9CA3AF "or click to browse · format: email|password per line"
  - Below 16px gap a "OR" divider with "OR" centered between 2 horizontal lines
  - Textarea bg #202020 radius 8px padding 12px, 200px tall, placeholder "Or paste accounts directly here..."

RIGHT panel (parsed accounts as cards):
- Header: "Loaded accounts" 14px/600 + counter pill green "12 accounts" 11px
- Scrollable list, each account card 56px tall, bg #1A1A1A radius 8px padding 12px, hover bg #1F1F1F:
  - Left: 32×32 circle with first letter of email, gradient bg #4F8EF7→#A78BFA
  - Middle: email 13px/500 #FAFAFA truncate + status indicator below 11px:
    • "Pending" with Lucide Clock #6B7280
    • "Running..." with Loader2 spinner #4F8EF7 (during)
    • "Success" with CheckCircle2 #22D26B
    • "Failed: <reason>" with XCircle #F87171
  - Right: 11px monospace "PROFILE_1" #6B7280 + 4px gap + Lucide MoreVertical icon

FOOTER row 16px gap:
- Left: progress bar 8px tall flex-1 bg #1F1F1F radius full, fill #22D26B gradient width 5/12. Above bar: text 11px "5 of 12 done · ~3 min remaining"
- Right: 2 buttons:
  - Secondary "Stop" 40px tall, bg #202020 border #2A2A2A radius 8px, only visible when running
  - Primary "Start Login All" 40px tall, bg #4F8EF7 text white 14px/600 padding 16px, Lucide Play icon

Below footer: collapsible log section "Show log ▼" — when expanded shows monospace black panel #0A0A0A radius 8px padding 12px, 200px tall, color #DCDCDC, 11px font. Auto-scroll latest line.

React + Tailwind + lucide-react + motion (stagger entrance per account card).
```

---

## 6️⃣ Prompt: Drive Settings Dialog

```
Generate Drive Sync Settings dialog for VEO Pipeline Pro.

Modal centered 720×640, bg #141414 radius 16px padding 32px.

HEADER: Lucide Cloud icon 24px #4F8EF7 + "Drive Sync" 18px/700 + close button right.

HERO section (top):

When NOT connected:
- Card bg gradient (45deg) rgba(79,142,247,0.08)→transparent, border 1px #2A2A2A, radius 12px, padding 24px
- Center content: Lucide CloudOff 40px #6B7280 + "Drive not connected" 16px/600 + "Connect to auto-upload generated videos" 13px #9CA3AF + small button "Connect" 32px tall #4F8EF7

When connected:
- Card same style but border-left 4px #22D26B accent
- Lucide CheckCircle2 24px #22D26B + "Connected" 14px/600 #22D26B
- Then row: avatar 24px circle "P" + "user@gmail.com" 14px/500 + folder name "VEO Output" + "Last sync 2 min ago" 12px #9CA3AF
- Right: small icon button "Disconnect" Lucide LogOut

3 ACTION CARDS in row (gap 16px), each card bg #1A1A1A radius 12px padding 20px hover bg #1F1F1F border #2A2A2A cursor-pointer:
1. Lucide Download 24px #4F8EF7 + title 14px/600 "Import from app.trbm.shop" + caption 11px #9CA3AF "Reuse Drive account configured on dashboard"
2. Lucide UserPlus 24px #A78BFA + "Connect new account" + "OAuth via browser sign-in"
3. Lucide FileJson 24px #FBBF24 + "Manual JSON" + "Upload service account file"

ADVANCED COLLAPSE (default closed) "Advanced settings ▼":
- Field "Output folder": input + Browse button + Auto-detect button (each input 36px bg #202020 radius 8px)
- Field "Drive folder ID": monospace input + Open Drive button (Lucide ExternalLink)
- Field "Telegram bot token" + "Telegram chat ID"
- Toggle "Enable auto-update from GitHub Releases" with Lucide RefreshCw icon

FOOTER: Right-aligned Cancel + primary "Save" button.

React + Tailwind + lucide-react.
```

---

## 7️⃣ Prompt: License Activation Dialog

```
Generate License Activation dialog for VEO Pipeline Pro.

Modal centered 480×560, bg #141414 radius 16px padding 32px shadow-2xl.

CONTENT vertical stack, 24px gap between sections:

1. ICON BLOCK (center): Lucide ShieldCheck 56px stroke-width 1.5 stroke #4F8EF7 inside circle bg rgba(79,142,247,0.1) 96×96 radius full. Center.

2. TITLE BLOCK (center text):
- "Activate VEO Pipeline Pro" 22px/700 letter-spacing -0.02em
- "Enter your license key to unlock all features" 13px #9CA3AF

3. MACHINE ID BLOCK:
- Label 11px/500 uppercase tracking-wider #6B7280 "MACHINE ID"
- Read-only field bg #1A1A1A border #2A2A2A radius 8px padding 12px, monospace 13px #4F8EF7 "36F9EF779405DB3F36CA40B4"
- Below right: copy button Lucide Copy 14px + "Copy" link 12px #4F8EF7

4. LICENSE INPUT:
- Label "LICENSE KEY"
- Input bg #202020 border #2A2A2A radius 8px padding 14px, monospace 14px #FAFAFA letter-spacing 0.05em
- Placeholder "XXXX-XXXX-XXXX-XXXX" #6B7280
- Auto-uppercase + auto-format with dashes every 4 chars

5. ACTIONS (vertical stack 12px gap):
- Primary button "Activate" 100% width 48px tall bg #4F8EF7 hover bg #6BA5FF text white 14px/600 radius 8px
- Below: text-link centered 12px "Need a license? — " + bold "Zalo 0345431884" link #4F8EF7

6. FOOTER (very bottom, very small):
- 11px #6B7280 center: "Truong Hoa · v5.1.5 · Commercial" with vertical bullet separators

NO CLOSE BUTTON — license is mandatory gate. User must Activate or quit app via OS.

React + Tailwind + lucide-react.
```

---

## 8️⃣ Prompt: Onboarding Wizard (4 steps)

```
Generate first-run Onboarding Wizard for VEO Pipeline Pro.

Modal centered 720×560, bg #141414 radius 16px shadow-2xl.

LAYOUT: vertical, no header. Content area 32px padding.

PROGRESS HEADER (top, 80px tall):
- 4 dots horizontal centered, gap 32px, line connecting dots
- Each dot: 24px circle, current=#4F8EF7 fill + ring, completed=#22D26B + Lucide Check inside, future=#2A2A2A border
- Below dots: step name "Welcome / Output / Integrations / Done"

CONTENT (varies per step):

STEP 1 — Welcome:
- Lucide Sparkles 64px #4F8EF7 center
- "Welcome to VEO Pipeline Pro" 24px/700 center
- Subtitle 14px #9CA3AF max-width 400px center "Let's get you set up. This wizard takes about 1 minute."
- 4 feature cards in 2x2 grid below (each card 140×100, bg #1A1A1A radius 8px padding 16px):
  - Lucide Wand2 #FF7A45 + "Generate" caption
  - Lucide Cloud #4F8EF7 + "Drive sync"
  - Lucide Send #A78BFA + "Telegram notify"
  - Lucide RefreshCw #22D26B + "Auto-update"

STEP 2 — Output folder:
- Lucide FolderOpen 48px #4F8EF7 center top
- "Where to save videos?" 18px/600 center
- 12px #9CA3AF "Choose folder for generated videos"
- Input field with default value "C:\Users\you\Documents\VEO Output" + Browse button right
- Below: 11px caption "Recommended: Documents folder for easy access"

STEP 3 — Integrations:
- Title "Optional integrations" 18px/600
- 3 collapsible cards stacked:
  - Drive Sync (icon Lucide Cloud) — expandable to show folder ID input + JSON file picker + "Import from app.trbm.shop" button
  - Telegram (Lucide Send) — bot token + chat ID inputs
  - Auto-update (Lucide RefreshCw) — checkbox "Enable update check on startup"

STEP 4 — Done:
- Lucide PartyPopper 64px #22D26B center
- "All set!" 24px/700
- 13px #9CA3AF "Click Finish to start using VEO Pipeline Pro"
- Below: 3 quick-tip rows with Lucide Lightbulb icons:
  - "Use ⌘K anywhere to search"
  - "Drive Sync uploads automatically when enabled"
  - "Auto-update checks GitHub on every launch"

FOOTER (sticky bottom, 64px tall, border-top 1px #2A2A2A):
- Left: "Skip setup" link 12px #9CA3AF
- Right: "Back" + "Next" / "Finish" buttons. Next = primary #4F8EF7

React + Tailwind + lucide-react. Use motion for step transitions (200ms slide).
```

---

## ⚙ Iteration tips

Sau khi paste mỗi prompt:
1. Generate → screenshot kết quả
2. Nếu xấu → paste lại screenshot + nói cụ thể: *"Make the cards more elevated, add stronger shadow. Increase prompt textarea to 280px tall. Use Lucide icons not emoji."*
3. Lặp 2-3 lần đến đẹp
4. Export Stitch project → gửi em port vào tool

---

**Author:** Truong Hoa · Zalo `0345431884`
**Repo:** https://github.com/ankaibua-spec/veo-pipeline
