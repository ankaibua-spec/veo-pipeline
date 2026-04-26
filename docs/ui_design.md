# VEO Pipeline Pro — UI Design Spec

Commercial-grade rebuild of the original `qt_ui/`. Located at `tool/qt_ui_modern/`.

## Design language

**Microsoft Fluent Design (dark)** — modern, professional, suitable for paid tool.

- **Layout:** Sidebar (240px) + topbar (56px) + content area (cards)
- **Color:** Deep dark `#1F1F1F` base, primary blue `#0078D4`, accent orange `#FF6B35`
- **Typography:** Segoe UI Variable (Windows native), Inter fallback
- **Density:** Comfortable padding (20-28px), 12px corner radius for cards
- **Motion:** Drop shadows + smooth hover transitions

## Architecture

```
launcher_pro.py
    ↓
splash.py        (2s branded splash)
    ↓
main_window.py   (sidebar + topbar + stacked content)
    ↓
pages/
    home          (stats dashboard, quick actions)
    text2video    (prompt + settings + generate)
    image2video   (placeholder)
    idea2video    (placeholder)
    character     (placeholder)
    create_image  (placeholder)
    grok          (placeholder)
    queue         (active jobs)
    history       (past gens)
    settings      (account, output, integrations)
```

## Files

| File | Purpose |
|------|---------|
| `theme.py` | Brand constants (colors, fonts, version, author) |
| `styles.py` | Global QSS stylesheet (Fluent dark) |
| `main_window.py` | MainWindow, Sidebar, TopBar, Pages |
| `splash.py` | Branded splash screen (gradient + version) |

## Branding

```python
APP_NAME      = "VEO Pipeline Pro"
APP_TAGLINE   = "Professional AI Video Generation Suite"
APP_VERSION   = "5.0.0"
APP_BUILD     = "Commercial"
AUTHOR        = "Truong Hoa"
AUTHOR_ZALO   = "0345431884"
SUPPORT_URL   = "https://zalo.me/0345431884"
```

## Run

```bash
cd tool
python launcher_pro.py
```

Old UI (`qt_ui/`) and entry (`run_veo_4.0.py`) kept for backward compatibility.

## TODO (next versions)

- [ ] Wire pages to existing workflow workers (`worker_run_workflow.py`, `A_workflow_*.py`)
- [ ] Light theme toggle
- [ ] Onboarding wizard for first-time setup
- [ ] System tray + minimize to background
- [ ] Real-time queue progress widget
- [ ] In-app YouTube preview after gen
- [ ] License activation dialog (commercial)
- [ ] Multi-language (vi/en)
- [ ] FFmpeg post-processing tab (overlay, subtitle, merge)
- [ ] Integration tab — config Drive folder, Telegram bot from UI

## Screenshots

(Pending — render after first run on Windows.)

## Migration path

`run_veo_4.0.py` → `launcher_pro.py` is opt-in. Both can coexist. When new pages reach feature parity with legacy `qt_ui/`, switch default entry.
