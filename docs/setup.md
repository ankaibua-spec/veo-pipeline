# Setup Guide

## 1. PC Windows side

### 1.1 Install Python + dependencies

```powershell
# Python 3.11+
winget install Python.Python.3.11

# Tool deps
pip install PyQt6 playwright requests urllib3
playwright install chromium

# Post-processor deps
pip install watchdog google-api-python-client google-auth
```

### 1.2 Get Google Drive service account JSON

1. Go to https://console.cloud.google.com → create project (or reuse existing)
2. Enable **Google Drive API**
3. Create service account → download JSON key
4. Save as `pc/drive_credentials.json`
5. Create Drive folder e.g. `VeoOutput` → share with service-account email (Editor)
6. Copy folder ID from URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`

### 1.3 Run tool

```powershell
cd tool
python run_veo_4.0.py
```

Tool opens GUI. Login Flow account once, token cached. Set `video_output_dir` to `C:\veo_output\` (or wherever).

### 1.4 Run post-processor (separate terminal)

```powershell
cd pc
set VEO_WATCH_DIR=C:\veo_output
set VEO_DRIVE_FOLDER_ID=YOUR_FOLDER_ID
set VEO_TG_BOT=YOUR_BOT_TOKEN
set VEO_TG_CHAT=YOUR_CHAT_ID
python post_processor.py
```

Now whenever tool gens a video → it auto syncs to Drive + notifies Telegram.

### 1.5 Auto-start (optional)

Use Windows Task Scheduler:
- Trigger: At log on
- Action: `python C:\path\to\pc\post_processor.py`

## 2. VPS Linux side

### 2.1 Service account credentials

```bash
# Reuse the same drive_credentials.json from PC
scp drive_credentials.json vps:/root/.veo_drive_creds.json
chmod 600 /root/.veo_drive_creds.json
```

### 2.2 Install deps

```bash
pip3 install google-api-python-client google-auth
```

### 2.3 Setup cron

```bash
sudo cp vps/veo_drive_pickup.py /opt/veo-pipeline/
echo 'VEO_DRIVE_FOLDER_ID=YOUR_FOLDER_ID' | sudo tee /etc/default/veo

cat <<EOF | sudo tee /etc/cron.d/veo-pickup
VEO_DRIVE_FOLDER_ID=YOUR_FOLDER_ID
*/5 * * * * root /usr/bin/python3 /opt/veo-pipeline/veo_drive_pickup.py >> /var/log/veo-pickup.log 2>&1
EOF
```

### 2.4 YouTube upload integration

The pickup script inserts into `english-pronunciation-factory.db` table `veo_drive_files`. The factory worker should pick up rows with `status='downloaded'` and run YouTube upload. (Manual integration step depending on factory codebase.)

## 3. Testing flow

1. Gen 1 video on PC via tool
2. Check `C:\veo_output\` has `.mp4`
3. Wait ~30s → post_processor renames, uploads Drive, Telegram notify
4. VPS cron next 5min → pickup → DB insert
5. Factory worker → YouTube upload
6. Telegram notify when uploaded

## 4. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tool says license invalid | `License.py` was bypassed; check it's the cleaned version |
| `pkill Chrome` kills your tabs | Run tool with separate browser profile, or patch `chrome_process_manager.py` to no-op |
| Drive upload fails | Service account needs Editor access to folder |
| Cron silent | Check `/var/log/veo-pickup.log` |
| Telegram fails | Verify bot token + chat ID; bot must be admin in channel |

## 5. Recommended folder structure on PC

```
C:\veo_pipeline\
├── tool\              ← RUN_VEO 4.0 source
├── pc\
│   ├── post_processor.py
│   ├── drive_credentials.json
│   └── veo_processed.json (auto-created)
└── veo_output\        ← tool saves here, watcher picks up
```
