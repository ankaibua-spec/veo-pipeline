"""
Post-processor: watch video_output_dir, rename + Drive upload + Telegram notify.
Runs alongside RUN_VEO 4.0. No core tool modification.

Setup PC:
1. pip install watchdog google-api-python-client google-auth-oauthlib requests
2. Place service-account JSON at: ./drive_credentials.json
3. Edit CONFIG section below
4. Run: python post_processor.py

Trigger: any new .mp4 in WATCH_DIR -> process.
"""
from __future__ import annotations
import os, re, sys, time, json, hashlib, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime

# ============ CONFIG ============
WATCH_DIR = Path(os.environ.get("VEO_WATCH_DIR", r"C:\veo_output"))
DRIVE_FOLDER_ID = os.environ.get("VEO_DRIVE_FOLDER_ID", "")  # thu muc Drive dich
DRIVE_CRED = Path(os.environ.get("VEO_DRIVE_CRED", "./drive_credentials.json"))
TG_BOT = os.environ.get("VEO_TG_BOT", "")
TG_CHAT = os.environ.get("VEO_TG_CHAT", "-1003375527350")  # kenh Video Veo3

# Thu muc luu state file (ngoai repo, tranh conflict git) - Fix #3
_STATE_DIR = Path.home() / ".veo_pipeline"
_STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)

PROCESSED_DB = _STATE_DIR / "veo_processed.json"

# Auto-update on startup + every N hours
# Fix #4: doi default sang "0" (opt-in, khong phai opt-out)
AUTO_UPDATE = os.environ.get("VEO_AUTO_UPDATE", "0") == "1"
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

# ThreadPoolExecutor dung chung cho watchdog handler - Fix #6
_executor = ThreadPoolExecutor(max_workers=2)


def load_processed():
    if PROCESSED_DB.exists():
        return json.loads(PROCESSED_DB.read_text())
    return {}


def save_processed(d):
    # Fix #5: ghi atomic (write tmp -> replace) de tranh file bi hong nua chung
    tmp = PROCESSED_DB.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2))
    os.replace(str(tmp), str(PROCESSED_DB))


def file_hash(p: Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def derive_topic(filename: str) -> str:
    """Extract topic from filename. Falls back to mtime-based name."""
    stem = Path(filename).stem
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
    """
    Tra ve:
      - drive_id (str)  : upload thanh cong
      - ""              : Drive khong duoc bat (DRIVE_FOLDER_ID trong)
      - None            : upload that bai (khong ghi DB)
    """
    if not DRIVE_FOLDER_ID:
        print("[drive] DRIVE_FOLDER_ID not set, skip upload")
        return ""  # Fix #2: phan biet "disabled" vs "failed"
    try:
        svc = drive_service()
        media = MediaFileUpload(str(p), mimetype="video/mp4", resumable=True)
        meta = {"name": p.name, "parents": [DRIVE_FOLDER_ID]}
        f = svc.files().create(body=meta, media_body=media, fields="id,name").execute()
        print(f"[drive] uploaded {p.name} -> id={f['id']}")
        return f["id"]
    except Exception as e:
        print(f"[drive] upload failed: {e}")
        return None  # None = that bai thuc su


def tg_notify(msg: str):
    # Fix #7: bo qua neu token trong de tranh 404
    if not TG_BOT or not TG_CHAT:
        # Telegram requires token in URL — see SECURITY.md, store onboarded.json with chmod 0600
        return
    try:
        url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"[tg] {e}")


def process_file(p: Path):
    if not p.exists() or p.stat().st_size < 100_000:
        return  # qua nho, bo qua

    # Fix #1: tang ong cho size-stability: 90 iter x 2s = 3 phut
    # So sanh ca size va mtime de dam bao file khong con duoc ghi
    last_size = -1
    last_mtime = -1.0
    for _ in range(90):
        try:
            st = p.stat()
            sz = st.st_size
            mt = st.st_mtime
        except OSError:
            return  # file bi xoa giua chung
        if sz == last_size and mt == last_mtime and sz > 100_000:
            break
        last_size = sz
        last_mtime = mt
        time.sleep(2)

    h = file_hash(p)
    db = load_processed()
    if h in db:
        return

    # Fix #1: boc rename trong try/except WindowsError/OSError
    # Neu rename that bai: log + skip (KHONG ghi hash) -> watchdog se thu lai
    try:
        new_p = rename_with_convention(p)
        print(f"[proc] {p.name} -> {new_p.name}")
    except (OSError, Exception) as e:
        print(f"[proc] rename failed ({p.name}): {e} — will retry on next event")
        return

    # Fix #2: chi ghi DB khi upload thanh cong hoac Drive bi tat chu y
    drive_id = drive_upload(new_p)

    if drive_id is None:
        # None = upload that bai thuc su -> KHONG ghi hash, watchdog se thu lai
        print(f"[proc] drive upload failed for {new_p.name} — skipping db write, will retry")
        return

    # drive_id la str (co the la "" neu Drive disabled, hoac id that)
    db[h] = {
        "original": p.name,
        "renamed": new_p.name,
        "size_mb": round(new_p.stat().st_size / 1024 / 1024, 1),
        "drive_id": drive_id,  # "" = Drive tat, "<id>" = thanh cong
        "ts": datetime.now().isoformat(),
    }
    save_processed(db)

    # Telegram notify
    msg = (
        f"\U0001f3ac <b>VEO video ready</b>\n"
        f"File: <code>{new_p.name}</code>\n"
        f"Size: {db[h]['size_mb']}MB\n"
        + (f"Drive: <code>{drive_id}</code>" if drive_id else "Drive: skipped")
    )
    tg_notify(msg)


class Handler(FileSystemEventHandler):
    """Fix #6: xu ly trong thread rieng, khong block dispatcher watchdog."""

    def _submit(self, path_str: str):
        p = Path(path_str)
        if p.suffix.lower() != ".mp4":
            return
        # Delay 3s roi submit vao pool de file co thoi gian flush
        def _delayed():
            time.sleep(3)
            try:
                process_file(p)
            except Exception as e:
                print(f"[watch] error processing {p.name}: {e}")
        _executor.submit(_delayed)

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"[watch] new file: {Path(event.src_path).name}")
        self._submit(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._submit(event.dest_path)


def auto_update_loop():
    if not AUTO_UPDATE:
        return
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
    print(f"[boot] State dir: {_STATE_DIR}")

    if AUTO_UPDATE:
        threading.Thread(target=auto_update_loop, daemon=True).start()

    for p in WATCH_DIR.glob("*.mp4"):
        process_file(p)

    obs = Observer()
    obs.schedule(Handler(), str(WATCH_DIR), recursive=True)
    obs.start()

    # Fix #3: restart_marker o ngoai repo dir
    restart_marker = _STATE_DIR / ".restart_required"
    try:
        while True:
            time.sleep(60)
            if restart_marker.exists():
                print("[boot] restart marker detected, exiting for relaunch")
                restart_marker.unlink(missing_ok=True)
                break
    except KeyboardInterrupt:
        pass
    obs.stop()
    # Fix #15: join voi timeout de tranh treo mai mai
    obs.join(timeout=30)
    if obs.is_alive():
        print("[boot] observer stuck, exiting anyway")


if __name__ == "__main__":
    main()
