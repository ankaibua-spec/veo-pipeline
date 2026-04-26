# VEO Pipeline

End-to-end video generation pipeline: **PC Windows tool generates Veo3 videos → Google Drive sync → VPS picks up → YouTube auto-upload**.

**Author:** Truong Hoa · Zalo `0345431884`

Bypasses Google Flow `UNUSUAL_ACTIVITY` block by running browser on residential IP (PC anh) instead of datacenter VPS.

## Architecture

```
PC Windows
├─ tool/        → RUN_VEO 4.0 GUI (cleaned, no telemetry)
├─ pc/          → post_processor.py (rename + Drive upload + Telegram notify)
└─ Google Drive Desktop sync

         ↓ Drive folder

VPS (Linux, 24/7)
├─ vps/         → veo_drive_pickup.py (poll Drive → download → queue)
└─ english-pronunciation-factory → YouTube upload
```

## Why this architecture

| Approach | UNUSUAL_ACTIVITY rate | Cost |
|----------|----------------------|------|
| Flow2API (datacenter proxy) | 100% blocked | $5-30/mo proxy |
| Vertex AI Veo3 official | 0% blocked | ~$960/mo |
| **PC tool + residential IP** | **<5%** | **free** |

Google trusts residential IP + real Chrome fingerprint of PC anh. Same fingerprint as manual login = no flag.

## Components

### `tool/` — RUN_VEO 4.0 cleaned

PyQt6 desktop app for generating Veo3 videos via labs.google.fx.

**Cleanups vs original:**
- ✅ Author personal info wiped
- ✅ Leaked OpenAI JWT token wiped (was already expired)
- ✅ License phone-home disabled
- ✅ Google Apps Script license server URL removed

Tabs: text-to-video, image-to-video, idea-to-video, character-sync, create-image, grok-text2video, grok-image2video.

### `pc/post_processor.py`

Watches tool's output folder. For each new `.mp4`:
1. Rename to `YYYY-MM-DD_HH-MM_<topic>.mp4` convention
2. Upload to Google Drive folder
3. Notify Telegram channel
4. Track in `veo_processed.json` (dedup)

### `vps/veo_drive_pickup.py`

Cron `*/5 * * * *` on VPS:
1. Poll Drive folder via service-account
2. Download new files → `/opt/english-pronunciation/storage/veo_pickup/`
3. Insert into `english-pronunciation-factory.db` table `veo_drive_files`
4. English Pronunciation Factory worker picks up → YouTube upload

## Setup

See [docs/setup.md](docs/setup.md) for full step-by-step.

**TL;DR:**

PC:
```bash
pip install PyQt6 playwright watchdog google-api-python-client requests
playwright install chromium
cd tool
python run_veo_4.0.py  # gen videos via GUI

# Separate terminal:
cd pc
set VEO_WATCH_DIR=C:\veo_output
set VEO_DRIVE_FOLDER_ID=<your-folder-id>
python post_processor.py
```

VPS:
```bash
pip3 install google-api-python-client google-auth
echo "VEO_DRIVE_FOLDER_ID=<id>" > /etc/default/veo
echo "*/5 * * * * root /usr/bin/python3 /opt/veo-pipeline/vps/veo_drive_pickup.py" > /etc/cron.d/veo-pickup
```

## Security

Tool was audited and cleaned. No backdoors, no exfiltration, no telemetry remaining. See [docs/audit.md](docs/audit.md) for findings.

⚠️ **Note:** `chrome_process_manager.py` calls `pkill Chrome` on tool start. Use a separate Chrome profile (e.g. Brave or Chrome Beta) to avoid losing your tabs.

## Auto-update

Both PC and VPS components include built-in auto-updater that pulls latest from this GitHub repo.

- PC: `pc/updater.py` runs every 6h in background while `post_processor.py` is alive. Restart auto.
- VPS: `vps/updater.sh` cron `0 */6 * * *`. Reload cron + Telegram notify on update.

Configure interval via env vars (see [docs/setup.md](docs/setup.md)).

## License

Original tool authored by Truong Hoa (Zalo 0345431884). Integration scripts MIT.
