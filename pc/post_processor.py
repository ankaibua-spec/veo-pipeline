"""
Post-processor: watch video_output_dir, rename + Drive upload + Telegram notify.
Runs alongside RUN_VEO 4.0. No core tool modification.

Setup PC:
1. pip install watchdog google-api-python-client google-auth-oauthlib requests
2. Place service-account JSON at: ./drive_credentials.json
3. Edit CONFIG section below
4. Run: python post_processor.py

Trigger: any new .mp4 in WATCH_DIR → process.
"""
from __future__ import annotations
import os, re, sys, time, json, hashlib, subprocess, threading
from pathlib import Path
from datetime import datetime

# ============ CONFIG ============
WATCH_DIR = Path(os.environ.get("VEO_WATCH_DIR", r"C:\veo_output"))
DRIVE_FOLDER_ID = os.environ.get("VEO_DRIVE_FOLDER_ID", "")  # target Drive folder
DRIVE_CRED = Path(os.environ.get("VEO_DRIVE_CRED", "./drive_credentials.json"))
TG_BOT = os.environ.get("VEO_TG_BOT", "8199167541:AAFun_6T7D0u-h2M5PygU0mIPOtj8OPRP5Y")
TG_CHAT = os.environ.get("VEO_TG_CHAT", "-1003375527350")  # Video Veo3 channel
PROCESSED_DB = Path("./veo_processed.json")
TOPIC_REGEX = re.compile(r"(?:^|_)(letter[_\s-]?\w|day|number|color|month|fruit|.*)\.mp4$", re.I)

# Auto-update on startup + every N hours
AUTO_UPDATE = os.environ.get("VEO_AUTO_UPDATE", "1") == "1"
AUTO_UPDATE_INTERVAL_H = int(os.environ.get("VEO_AUTO_UPDATE_INTERVAL_H", "6"))
# ================================

import requests
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("Install: pip install google-api-python-client google-auth")
    sys.exit(1)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Install: pip install watchdog")
    sys.exit(1)


def load_processed():
    if PROCESSED_DB.exists():
        return json.loads(PROCESSED_DB.read_text())
    return {}


def save_processed(d):
    PROCESSED_DB.write_text(json.dumps(d, indent=2))


def file_hash(p: Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def derive_topic(filename: str) -> str:
    """Extract topic from filename. Falls back to mtime-based name."""
    # Strip prefix like 'video_xxx_' and suffix '.mp4'
    stem = Path(filename).stem
    # Remove timestamps / UUIDs
    stem = re.sub(r"\b\d{8,}\b", "", stem)
    stem = re.sub(r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b", "", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem[:50] or "untitled"


def rename_with_convention(p: Path) -> Path:
    """Rename to YYYY-MM-DD_HH-MM_<topic>.mp4"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    topic = derive_topic(p.name)
    new_name = f"{ts}_{topic}.mp4"
    new_path = p.parent / new_name
    if new_path.exists():
        new_name = f"{ts}_{topic}_{file_hash(p)[:6]}.mp4"
        new_path = p.parent / new_name
    p.rename(new_path)
    return new_path


def drive_service():
    creds = service_account.Credentials.from_service_account_file(
        str(DRIVE_CRED), scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def drive_upload(p: Path) -> str | None:
    if not DRIVE_FOLDER_ID:
        print("[drive] DRIVE_FOLDER_ID not set, skip upload")
        return None
    try:
        svc = drive_service()
        media = MediaFileUpload(str(p), mimetype="video/mp4", resumable=True)
        meta = {"name": p.name, "parents": [DRIVE_FOLDER_ID]}
        f = svc.files().create(body=meta, media_body=media, fields="id,name").execute()
        print(f"[drive] uploaded {p.name} → id={f['id']}")
        return f["id"]
    except Exception as e:
        print(f"[drive] upload failed: {e}")
        return None


def tg_notify(msg: str):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"[tg] {e}")


def process_file(p: Path):
    if not p.exists() or p.stat().st_size < 100_000:
        return  # too small, skip

    # Wait until file size stable (gen still writing)
    last_size = -1
    for _ in range(30):
        sz = p.stat().st_size
        if sz == last_size and sz > 100_000:
            break
        last_size = sz
        time.sleep(2)

    h = file_hash(p)
    db = load_processed()
    if h in db:
        return

    # Rename
    new_p = rename_with_convention(p)
    print(f"[proc] {p.name} → {new_p.name}")

    # Drive upload
    drive_id = drive_upload(new_p)

    # Save state
    db[h] = {
        "original": p.name,
        "renamed": new_p.name,
        "size_mb": round(new_p.stat().st_size / 1024 / 1024, 1),
        "drive_id": drive_id,
        "ts": datetime.now().isoformat(),
    }
    save_processed(db)

    # Telegram notify
    msg = (
        f"🎬 <b>VEO video ready</b>\n"
        f"File: <code>{new_p.name}</code>\n"
        f"Size: {db[h]['size_mb']}MB\n"
        + (f"Drive: <code>{drive_id}</code>" if drive_id else "Drive: skipped")
    )
    tg_notify(msg)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        if p.suffix.lower() == ".mp4":
            print(f"[watch] new file: {p.name}")
            time.sleep(3)
            process_file(p)

    def on_moved(self, event):
        if event.is_directory: return
        p = Path(event.dest_path)
        if p.suffix.lower() == ".mp4":
            time.sleep(3)
            process_file(p)


def auto_update_loop():
    if not AUTO_UPDATE: return
    updater = Path(__file__).parent / "updater.py"
    while True:
        try:
            print("[update] checking...")
            subprocess.run([sys.executable, str(updater)], timeout=60)
        except Exception as e:
            print(f"[update] {e}")
        time.sleep(AUTO_UPDATE_INTERVAL_H * 3600)


def main():
    if not WATCH_DIR.exists():
        WATCH_DIR.mkdir(parents=True)
    print(f"[boot] Watching: {WATCH_DIR}")
    print(f"[boot] Drive folder: {DRIVE_FOLDER_ID or '(not set)'}")
    print(f"[boot] Auto-update: {AUTO_UPDATE} every {AUTO_UPDATE_INTERVAL_H}h")

    if AUTO_UPDATE:
        threading.Thread(target=auto_update_loop, daemon=True).start()

    for p in WATCH_DIR.glob("*.mp4"):
        process_file(p)

    obs = Observer()
    obs.schedule(Handler(), str(WATCH_DIR), recursive=True)
    obs.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    main()
