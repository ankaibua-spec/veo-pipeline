# STITCH PROMPTS — Mobile → Desktop Conversion

Mục đích: tái sử dụng 4 màn hình mobile Stitch đã có (License / Onboarding / Bulk Login / Drive Settings) → chuyển thành **Desktop 1440×880** giữ Linear/Spotify aesthetic.

Cách dùng: paste **MASTER DIRECTIVE** một lần, sau đó paste 4 prompt theo thứ tự. Mỗi prompt yêu cầu Stitch giữ nguyên content/logic của bản mobile cũ, chỉ relayout sang desktop.

---

## MASTER DIRECTIVE (paste 1 lần đầu)

```
You previously generated mobile (~390px) screens for VEO Pipeline Pro: License Activation, Onboarding Wizard, Bulk Login Manager, Drive Sync Settings.

Now I need DESKTOP versions. Rules:

CANVAS: 1440 × 880 fixed. Not responsive. Not mobile.

DESIGN SYSTEM (locked):
- Background: #0B0B0F (window), #111116 (panel/card), #16161D (input field)
- Border: #1F1F28 (1px hairline)
- Text: #FAFAFA (primary), #A1A1AA (secondary), #71717A (muted)
- Accent: #FF6B35 (orange — primary CTA only), hover #FF8159
- Success: #22C55E, Warning: #FACC15, Error: #EF4444
- Font: Inter (UI), JetBrains Mono (code/keys/IDs)
- Radius: 8px buttons, 12px cards, 16px modals
- Shadow on modals: 0 24px 48px rgba(0,0,0,0.6)
- Motion: 200ms ease-out, no bouncy springs

LAYOUT PRINCIPLES (desktop):
- Modal/Dialog screens (License, Onboarding, Bulk Login, Drive Settings) appear as CENTERED OVERLAYS over a dimmed app backdrop (rgba(0,0,0,0.7) + backdrop-blur-sm).
- The backdrop shows a faint sidebar (256px) + content area behind, indicating these are app-modals not standalone pages.
- Content INSIDE modals uses two-column or table layouts where possible — utilize horizontal space, not vertical scroll.
- Buttons live in a footer bar (right-aligned for primary action).
- Headers: 24-28px semibold, with optional inline icon + small description below.

STACK:
- React + TypeScript + Tailwind v4 + Lucide React icons + Motion library.
- Export as ZIP (project files) per screen.

KEEP FROM MOBILE: all functionality, all field labels, all copy text, all validation rules. Just reflow for desktop.
```

---

## PROMPT #1 — License Activation (Desktop modal)

```
Convert your mobile License Activation screen → Desktop modal.

DIMENSIONS:
- Outer: 1440×880 with dimmed app backdrop visible behind.
- Modal card: 560×auto, centered, bg #111116, border 1px #1F1F28, radius 16px, shadow 0 24px 48px rgba(0,0,0,0.6).

CONTENT (keep from mobile):
- Brand lockup top: VEO Pipeline Pro icon (32×32 orange gradient square w/ play triangle) + "VEO Pipeline Pro" 20px semibold + "Commercial Edition v5.1.5" 12px muted underneath.
- Title: "Activate License" 24px semibold.
- Subtitle: "Enter your license key to unlock all features." 14px secondary.
- License key input: full-width, h-14, bg #16161D, border #1F1F28, focus border #FF6B35, font JetBrains Mono 16px, placeholder "XXXX-XXXX-XXXX-XXXX", auto-uppercase, dash auto-insert every 4 chars.
- Machine ID display: small box below input, label "This Machine" 12px muted + value "B4F2-9A1C-..." in mono 13px primary, with copy icon button on right (lucide Copy).
- Status row (conditional, hidden by default):
  - Validating: spinner + "Verifying license..."
  - Success: green check icon + "License valid — expires Apr 27, 2027"
  - Error: red x icon + error message in #EF4444
- Footer (full-width, separated by 1px #1F1F28 border-top, p-6):
  - Left: text button "Buy License" (orange link, 14px, opens browser to zalo.me/0345431884)
  - Right: primary button "Activate" (h-10, px-6, bg #FF6B35 hover #FF8159, white text, semibold, disabled state grey when key invalid format).
- Top-right close button: ghost icon button (lucide X), 36×36, hover bg #1F1F28.

INTERACTIONS:
- Modal entry: scale 0.96→1.0 + opacity 0→1 over 200ms ease-out. Backdrop fades in 150ms.
- Input focus ring: 2px #FF6B35 with 0.4 opacity outer glow.
- Activate button shows inline spinner replacing label during validation.
- Success state: card flashes green border for 600ms then auto-dismisses after 1.5s.

Generate ZIP.
```

---

## PROMPT #2 — Onboarding Wizard (Desktop modal, 4 steps)

```
Convert your mobile Onboarding Wizard → Desktop modal with horizontal stepper.

DIMENSIONS:
- Modal card: 880×600, centered, bg #111116, radius 16px, shadow 0 24px 48px rgba(0,0,0,0.6).
- Backdrop: dimmed app behind.

LAYOUT:
- Top bar (h-16, border-bottom #1F1F28, px-8, flex items-center justify-between):
  - Left: "Setup Wizard" 18px semibold + "Step {current} of 4" 13px muted.
  - Right: ghost X close button.
- Stepper (h-14, px-8, border-bottom #1F1F28):
  - 4 circular nodes (32×32) connected by 1px lines.
  - Past steps: filled #FF6B35 with white check icon.
  - Current: filled #FF6B35 with white number, ring 4px rgba(255,107,53,0.2).
  - Future: bg #16161D, border #1F1F28, muted number.
  - Labels under each: 12px secondary ("Welcome" / "API Keys" / "Drive Sync" / "Done").
- Body (flex-1, p-10, scrollable if needed):
  - Step content area, max-width 600px center-aligned text+inputs.
- Footer (h-16, border-top #1F1F28, px-8, flex justify-between):
  - Left: ghost button "Back" (disabled on step 1, lucide ChevronLeft + label).
  - Right: primary "Next" (orange, ChevronRight) or "Finish" (step 4).

STEP CONTENT (keep from mobile):

Step 1 — Welcome:
- Large icon (96×96 orange gradient circle with Sparkles).
- H2 "Welcome to VEO Pipeline Pro" 28px.
- Paragraph "Let's set up your workspace in 3 quick steps." 15px secondary, max 480px.
- 3-row feature list with check icons: "Generate Veo3 videos in batch", "Auto-sync to Google Drive", "Manage 100+ Flow accounts".

Step 2 — API Keys:
- H3 "Connect Your Services" 20px.
- 4 input groups stacked: Gemini API Key / OpenAI API Key (optional) / TwelveData (optional) / Telegram Bot Token (optional).
- Each: label 14px + small help link "Get key" (orange, opens external) + password-masked input with show/hide toggle.
- Inline validation badge per row (green check / red x / grey "—").

Step 3 — Drive Sync:
- H3 "Google Drive Integration" 20px.
- Two stacked cards (border #1F1F28, p-5, radius 12):
  - Card A "OAuth (recommended)": Google G logo + "Sign in with Google" button (white bg, dark text).
  - Card B "Service Account JSON": dashed-border drop zone (h-32, lucide Upload icon center + "Drop credentials.json or click to browse").
- Below: input "Default Drive Folder ID" with "Browse..." button (opens Drive picker — represent as ghost button placeholder).

Step 4 — Done:
- Center: large green check circle (96×96).
- H2 "All Set!" 28px.
- Paragraph "Your workspace is ready. Start generating videos now." secondary.
- Single primary button "Open Dashboard" centered (replaces footer Next).

INTERACTIONS:
- Step transition: slide horizontal 300ms ease-out (incoming from right, outgoing to left). On Back: reverse.
- Stepper node click: only allow going back to completed steps.
- Footer button states: Back disabled on step 1, Next disabled until step validation passes.

Generate ZIP.
```

---

## PROMPT #3 — Bulk Login Manager (Desktop modal with table)

```
Convert your mobile Bulk Login → Desktop modal featuring a real data table.

DIMENSIONS:
- Modal card: 1120×720, centered, bg #111116, radius 16px.

LAYOUT:
- Top bar (h-16, px-8, border-bottom #1F1F28, flex justify-between):
  - Left: lucide Users icon (24px orange) + "Bulk Login Manager" 18px semibold + chip "{count} accounts" (small bg #16161D, border #1F1F28, text muted, 12px, ml-3).
  - Right: ghost X close.
- Toolbar (h-14, px-8, border-bottom #1F1F28, flex gap-3):
  - Primary "Login All" button (orange, lucide LogIn).
  - Ghost "Stop" (disabled unless running, lucide Square).
  - Divider.
  - Ghost "Add Account" (lucide Plus).
  - Ghost "Import CSV" (lucide Upload).
  - Ghost "Export" (lucide Download).
  - Spacer flex-1.
  - Search input (w-64, h-9, bg #16161D, lucide Search left icon, placeholder "Search by email...").
  - Filter dropdown (chip-style, "Status: All" + ChevronDown).

TABLE:
- Header row (h-11, sticky, bg #16161D, text 12px uppercase tracking-wide muted, px-8):
  - Columns: Checkbox (40px) | Email (flex-1) | Proxy (200px) | Status (140px) | Last Login (160px) | Actions (80px).
- Body rows (h-12, hover bg #16161D, border-bottom #1F1F28, px-8):
  - Checkbox.
  - Email (mono 13px primary).
  - Proxy host:port (mono 12px muted).
  - Status badge: pill h-6 px-2 radius-full, bold 11px:
    - Idle: bg #1F1F28, text muted
    - Logging in: bg rgba(250,204,21,0.15), text #FACC15, with pulsing dot
    - Success: bg rgba(34,197,94,0.15), text #22C55E, check icon
    - Error: bg rgba(239,68,68,0.15), text #EF4444, x icon
  - Last login: relative time "2h ago" 13px secondary.
  - Actions: 3-dot menu (lucide MoreHorizontal) on hover.
- Empty state (when no accounts): center-aligned, lucide UserPlus icon (48px muted) + "No accounts yet" 16px + "Click 'Add Account' to start" 13px muted + ghost "Import CSV" button.

PROGRESS BAR (when "Login All" running):
- Sticky band above footer (h-12, bg #16161D, border-top #1F1F28, px-8):
  - Left: "Logging in 12 of 47 accounts" 13px.
  - Center: linear progress bar (flex-1 max-w-md, h-1.5, bg #1F1F28, fill #FF6B35).
  - Right: ETA "~3m remaining" 13px muted.

FOOTER:
- (h-14, px-8, border-top #1F1F28, flex justify-between):
- Left: "{selected} selected" 13px muted (or empty).
- Right: primary "Close" ghost button.

INTERACTIONS:
- Row checkbox: select; bulk-actions toolbar appears (slide down 200ms) showing "Login Selected / Delete Selected" buttons.
- Row hover: bg #16161D, action menu becomes visible.
- Status badge "Logging in" has pulsing dot (1s ease-in-out infinite).
- Error rows can be expanded to show error detail (chevron caret on left, accordion 250ms).

Generate ZIP.
```

---

## PROMPT #4 — Drive Sync Settings (Desktop modal, two-column)

```
Convert your mobile Drive Sync Settings → Desktop modal, two-column layout.

DIMENSIONS:
- Modal card: 960×640, centered, bg #111116, radius 16px.

LAYOUT:
- Top bar (h-16, px-8, border-bottom #1F1F28):
  - lucide HardDrive icon (24px) + "Drive Sync Settings" 18px semibold.
  - Status pill on right: green dot + "Connected" or grey + "Not connected".
  - Ghost X close.
- Body: 2 columns (border-right #1F1F28 between, h-full):
  - LEFT COL (w-64, p-6, bg #0E0E13):
    - Vertical nav (radius 8 hover bg #16161D, active state bg #1F1F28 with orange left-border 3px):
      - "Account" (lucide User)
      - "Folders" (lucide Folder)
      - "Sync Rules" (lucide Settings2)
      - "Schedule" (lucide Clock)
    - Each row: 14px primary, h-10, px-3, gap-3.
  - RIGHT COL (flex-1, p-8, scrollable):
    - Section title 18px semibold + 13px secondary description.
    - Form fields below.

CONTENT PER TAB (keep mobile content):

ACCOUNT tab:
- Card "Connected Account" (border #1F1F28, p-5, radius 12):
  - Google G avatar (40×40) + email "user@gmail.com" 14px primary + "Connected via OAuth" 12px muted.
  - Right: ghost "Disconnect" button (red text, hover bg rgba(239,68,68,0.1)).
- Below: ghost button "Import from app.trbm.shop" with lucide Globe icon — pulls OAuth refresh_token + drive_id from VPS endpoint.
- Below: alternative "Use Service Account" expandable section (chevron toggle):
  - Drop zone (h-32 dashed) for credentials.json.

FOLDERS tab:
- Field "Default Drive Folder":
  - Read-only input showing folder name + ID + "Browse..." button on right.
- Sub-folders list (table):
  - Columns: Pipeline (English Shorts / Pronunciation / etc.) | Folder | Auto-create new files toggle.
- Footer-row "Add Pipeline Mapping" ghost button.

SYNC RULES tab:
- Toggles list (each row h-12, border-bottom #1F1F28):
  - "Auto-sync new videos" — switch right.
  - "Delete from local after sync" — switch.
  - "Compress before upload" — switch.
  - "Notify on sync errors" — switch.
- Section "File Filters":
  - Multi-select chips for extensions (.mp4 / .mov / .json / etc.).

SCHEDULE tab:
- Radio group: "Realtime (watcher)" / "Every {N} minutes" / "Daily at {HH:MM}" / "Manual only".
- Time picker / number input depending on selection.
- "Last synced" timestamp 13px muted at bottom.

FOOTER:
- (h-14, px-8, border-top #1F1F28):
- Left: "All changes saved" 13px muted with check icon (or "Unsaved changes" #FACC15).
- Right: ghost "Cancel" + primary "Save Changes" (orange).

INTERACTIONS:
- Switch toggle: 200ms ease, knob slides + bg color cross-fades.
- Save button: spinner during write, success flash green for 600ms.
- Tab switch: instant content swap, no animation (Linear-style).
- "Disconnect" requires confirmation popover (small floating card with "Disconnect Drive?" + Cancel/Confirm).

Generate ZIP.
```

---

## CHECKLIST sau khi nhận đủ 4 ZIP

- [ ] License Activation — Desktop modal 560 wide
- [ ] Onboarding Wizard — Desktop modal 880×600 với horizontal stepper
- [ ] Bulk Login — Desktop modal 1120×720 với data table
- [ ] Drive Sync Settings — Desktop modal 960×640 hai cột

Sau đó port toàn bộ vào `tauri/src/screens/` cùng 8 màn hình từ V2 + V3 → build Tauri t6.0.0.

---

## TIPS

- Nếu Stitch trả về thiếu `package.json` → bảo "include full project files including package.json, tsconfig.json, vite.config.ts, and src/main.tsx".
- Nếu Stitch dùng padding mobile (px-4) → bảo "use desktop padding px-8 minimum, p-10 for hero areas".
- Nếu Stitch trả responsive grid → bảo "fixed 1440px width, no @media queries, no responsive classes — desktop only".
- Backdrop should match prior screens: `bg-black/70 backdrop-blur-sm` over a faint app shell snapshot (sidebar 256px + main area).
