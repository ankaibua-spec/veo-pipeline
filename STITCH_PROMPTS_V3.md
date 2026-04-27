# Stitch Prompts V3 — Polish + Edge Cases

Bổ sung cho `STITCH_PROMPTS_READY.md`. Tập trung vào **states thiếu** + **micro-screens**.

Paste master directive trước → paste từng prompt bên dưới.

---

## 9️⃣ Settings — API Keys section

```
Generate the API Keys sub-section of Settings page for VEO Pipeline Pro desktop.

Context: Settings page already has 30/70 split. Right side renders the section based on left nav. This shows what right side displays when "API Keys" is active in left nav.

LAYOUT vertical stack with 24px gap, 48px padding:

Header row:
- Title 24px/700 "API Keys"
- Subtitle 13px #9CA3AF "Manage credentials for external AI services"

Card "Active Providers" (bg #141414 radius 12 padding 24):
- Table-style rows, each 64px tall, dividers 1px #2A2A2A:
  - Row 1: 32px provider logo (Veo3 Google, Grok x.ai logo, Sora OpenAI, Kie.ai favicon, Groq logo)
  - Provider name 14px/600 + status pill ("Connected" green / "Not configured" gray)
  - Masked key display: monospace "sk_live_••••••••••••a8f2" 12px #6B7280
  - Right actions: "Test connection" button (small, ghost) + "Edit" pencil icon + "Remove" trash icon

Card "Add New Provider":
- Dropdown "Select provider..." with logos
- Input field appears with provider-specific placeholder ("Paste your API key...")
- "Test & Save" primary button #4F8EF7

Card "Usage This Month" small at bottom:
- Bar chart Recharts-style, x-axis = providers, y-axis = USD spent. Total caption below.

Use Lucide for actions. NO emoji. Tailwind v4 React 19.
```

---

## 🔟 Settings — Models section

```
Generate the Models sub-section of Settings page for VEO Pipeline Pro.

LAYOUT 48px padding, 24px gap stack:

Header:
- "Model Configuration" 24px/700
- "Default models per pipeline + cost preview" 13px #9CA3AF

Card "Default Models" — 4 dropdowns side-by-side in 2×2 grid (or stack on narrow):
- Each cell: label "Text → Video" / "Image → Video" / "Idea → Video" / "Character Sync"
- Dropdown showing current default ("Veo 3.1 Quality" with badge "100 credits")
- Each option in dropdown shows: name + tier badge + cost per video

Card "Cost Calculator":
- 3 input rows side-by-side:
  - "Videos per day" stepper [10]
  - "Days per month" stepper [30]  
  - "Average duration" select (4s/6s/8s)
- Live computed result big number 48px/700 #4F8EF7: "9,000 credits/month"
- Below: "≈ $35 / month" muted

Card "Quality Presets" (3 preset cards in row):
- "Eco" — Lite model, 4s, $0.10/video
- "Standard" — Fast model, 6s, $0.30/video (default highlighted with #4F8EF7 border)
- "Premium" — Quality model, 8s, $0.80/video
- Each card with radio button + click to select

NO mock data hardcoded — use placeholder strings like "{model_name}" so dev can wire later.
```

---

## 1️⃣1️⃣ Notifications panel (slide-out from top bar bell)

```
Generate the Notifications panel slide-out for VEO Pipeline Pro.

Trigger: clicking bell icon in top bar. Panel slides from right edge.

PANEL: 400px wide, full height (under top bar = 64px), bg #141414, border-left 1px #2A2A2A.

Header (sticky, 56px tall, padding 20px):
- "Notifications" 16px/600
- Right: "Mark all read" 12px link #4F8EF7 + close X button

Tabs (sticky below header):
- "All (12)" / "Unread (3)" — pill toggle group
- Filter dropdown "All types" right-aligned

Notification list (scroll):
Each item 80px tall, padding 16px, border-bottom 1px #2A2A2A, hover bg #1A1A1A:
- Left: 32px circle icon based on type:
  • Generation done — green CheckCircle2
  • Generation failed — red XCircle
  • Update available — blue Sparkles
  • Bulk login complete — purple Users
  • Drive sync — cyan Cloud
- Middle stack:
  - Title 13px/600
  - Description 12px #9CA3AF (truncate 2 lines)
  - Timestamp 11px #6B7280 "2 min ago"
- Right: dot indicator (#4F8EF7 6px) if unread + kebab menu

Empty state when no notifications:
- Lucide BellOff 48px #2A2A2A center
- "No notifications" 14px #9CA3AF
- "You're all caught up" 12px #6B7280

Footer:
- "Notification settings →" link 12px #4F8EF7

Motion: slide-in 250ms cubic-bezier from right.
```

---

## 1️⃣2️⃣ Cmd+K Command Palette

```
Generate Cmd+K command palette for VEO Pipeline Pro (Linear-inspired).

Modal: dim overlay rgba(0,0,0,0.6) blur-md. Centered 640×480, vertical-anchored 20% from top.

Container bg #141414 radius 12 shadow-2xl border 1px #2A2A2A.

Header:
- 56px tall search bar bg transparent
- Left: Lucide Search 18px #6B7280
- Input 15px placeholder "Search commands, prompts, settings..."
- Right: kbd hint "ESC" 11px monospace

Divider 1px #2A2A2A

Results section (max 320px, scroll):
Group sections, each:
- Section header sticky 11px uppercase tracking-wider #6B7280 "RECENT" / "COMMANDS" / "NAVIGATION" / "PROMPTS"
- Items each 44px tall, padding 12px 16px:
  - Left: Lucide icon 16px (matches command type)
  - Middle: command label 14px + optional description 11px #6B7280
  - Right: keyboard shortcut "⌘G" or "→" arrow if it's nav

Sample items:
COMMANDS:
- "Generate new video" with Wand2 + ⌘N
- "Open queue" with ListChecks + ⌘3
- "Run bulk login" with Users + ⇧⌘L

NAVIGATION:
- "Go to Home" with Home + ⌘1
- "Go to Settings" with Settings + ⌘,

PROMPTS (recently used):
- "a young female English teacher pronouncing..." truncate
- "cinematic ocean sunset, slow zoom..."

Selected item bg rgba(79,142,247,0.15) border-l 2px #4F8EF7 text #FAFAFA
Default item text #9CA3AF, hover bg #1A1A1A

Footer (40px, sticky bottom):
- 11px caption left: "↑↓ navigate · ↵ select · ⌘K open"
- Right: "Powered by VEO Pipeline Pro"

Motion: fade-in 200ms + scale 0.96→1.
```

---

## 1️⃣3️⃣ Toast notification (corner stack)

```
Generate toast notification component for VEO Pipeline Pro.

Stacked top-right, 16px from edge, 8px gap between toasts.

EACH TOAST: 360px wide, min-height 64px, max-height 120px. bg #141414 border 1px #2A2A2A radius 12 shadow 0 8px 24px rgba(0,0,0,0.5) padding 16px.

Layout: horizontal flex 12px gap.
- Left: 32×32 icon circle based on type:
  • Success: bg rgba(34,210,107,0.15) + Lucide CheckCircle2 18px #22D26B
  • Error: bg rgba(248,113,113,0.15) + XCircle 18px #F87171
  • Warning: bg rgba(251,191,36,0.15) + AlertTriangle 18px #FBBF24
  • Info: bg rgba(79,142,247,0.15) + Info 18px #4F8EF7
- Middle stack flex-1:
  - Title 14px/600 #FAFAFA "Video generated successfully"
  - Description 12px #9CA3AF "the_letter_d.mp4 saved to Downloads"
  - Optional action link 12px #4F8EF7 "View in queue →"
- Right: small close X button 14px #6B7280 hover #FAFAFA

Progress bar at bottom of toast (if auto-dismiss): 2px tall, full width, bg gradient from icon-color, animated countdown over 4s.

Motion:
- Enter: slide-in from right 280ms + fade
- Exit: slide-right 200ms + fade
- Stack reflow: 200ms ease

Variants needed: success, error, warning, info, progress (with spinner instead of icon — for "Uploading...").

Container = toast.tsx + provider.tsx for global use.
```

---

## 1️⃣4️⃣ About / Help modal

```
Generate About modal for VEO Pipeline Pro.

Modal centered 560×480, bg #141414 radius 16 padding 32 shadow-2xl.

LAYOUT vertical center:

1. Brand block:
- 48px diamond/spark gradient icon (#4F8EF7→#A78BFA) center
- "VEO Pipeline Pro" 24px/700 letter-spacing -0.02em center
- "v5.1.5 · Commercial Edition" 12px #9CA3AF center

2. Divider

3. Info grid 2 columns:
- Left col: "Author" / "Email" / "Website"
- Right col: "Truong Hoa" / "truonghoa@gmail.com" / "github.com/ankaibua-spec/veo-pipeline" (link)

4. Description center, max 400px:
"Professional AI video generation pipeline with Veo3 + Grok integration. Bulk account management, Drive sync, YouTube upload automation."

5. Stats row centered, 4 small metric cards 80×60:
- Build: monospace "5e6f8a3"
- Released: "Apr 27, 2026"
- Platform: "Windows x64"
- License: "Active"

6. Quick links row:
- "Documentation" / "Changelog" / "Report Bug" / "Zalo Support 0345431884" — all Lucide ExternalLink with text 12px #4F8EF7

7. Bottom-right small button "Check for updates" with Lucide RefreshCw

8. Bottom-left disclaimer 11px #6B7280:
"© 2026 Truong Hoa. All rights reserved."

NO emoji. Lucide icons only. 200ms scale fade-in.
```

---

## 1️⃣5️⃣ Update progress dialog

```
Generate Update Progress dialog for VEO Pipeline Pro auto-update flow.

Modal centered 480×320, no close button (mandatory completion).

CONTENT vertical:

1. Top icon: Lucide Download 48px #4F8EF7 with subtle animation (pulsing scale 1→1.05 every 2s)

2. Title 18px/600 center "Updating to v5.1.6"
3. Subtitle 13px #9CA3AF center "Please don't close the app"

4. Progress block (full width):
- Stage label 12px #9CA3AF: "Downloading installer..." → "Verifying signature..." → "Extracting files..." → "Restarting..."
- Progress bar 6px tall, bg #1A1A1A radius full, fill gradient #4F8EF7→#A78BFA animated stripe
- Below bar: 11px stats row split:
  - Left: "12.4 MB / 103 MB"
  - Right: "2.3 MB/s · 40s remaining"

5. Completed-stages checklist below progress (4 items):
- ✓ Connected to GitHub Releases (#22D26B)
- ◐ Downloading installer (#4F8EF7 pulsing)
- ○ Verifying signature (#6B7280 dim)
- ○ Restarting (#6B7280 dim)

6. Bottom: small note 11px #6B7280 center
"App will close and restart automatically when complete"

NO cancel button (this update is critical / from user accept).

State variants for design:
- Initial: stage 0%
- Downloading: stage 1, 40% bar
- Done: all green checks, button "Restart now" appears (primary 40px tall)

Motion: progress bar smooth animation, stage transitions 300ms cross-fade.
```

---

## 1️⃣6️⃣ Empty states (various)

```
Generate 5 empty state illustrations for VEO Pipeline Pro screens.

EACH EMPTY STATE: vertical center stack, max-width 320px, gap 16px.

1. Empty Queue (when no jobs):
- Lucide ListChecks 56px stroke-width 1, color #2A2A2A (very subtle, line-art look)
- Title 16px/600 #9CA3AF "No jobs in queue"
- Description 12px #6B7280 max-width 280px center: "Generated videos appear here. Click 'Generate' to start your first one."
- CTA button "Start Generating" small 32px #4F8EF7 with Lucide Wand2

2. Empty History (no past):
- Lucide History 56px #2A2A2A
- "No history yet"
- "Your past generations will appear here once you create your first video."

3. Empty Search (no results):
- Lucide SearchX 56px #2A2A2A
- "No results"
- "Try different keywords or check your filters."
- Small ghost button "Clear filters"

4. Drive not connected:
- Lucide CloudOff 56px #2A2A2A
- "Drive not connected"
- "Connect Google Drive to auto-upload generated videos."
- CTA "Connect Drive" 32px #4F8EF7 with Cloud icon

5. License expired:
- Lucide ShieldAlert 56px #FBBF24 (warning color, not muted — this matters)
- "License expired"
- "Renew your license to continue generating videos."
- CTA "Renew now" 32px #4F8EF7

ALL empty states use line-art style icons (stroke-width 1), muted colors except where action urgency (#FBBF24/#F87171). Consistent typography hierarchy. NO illustrations or images — pure icon + text + CTA.
```

---

## 📦 Workflow

1. Mở Stitch → paste Master Directive vào Context (1 lần đầu)
2. Paste prompt #9 → generate → screenshot → iterate 1-2 lần
3. Lặp prompt #10 → #16
4. Export tất cả → gửi em qua Telegram
5. Em port vào Tauri trong session sau

---

**Total v1+v2+v3 = 16 prompts** đã có. Đủ cover full app.
