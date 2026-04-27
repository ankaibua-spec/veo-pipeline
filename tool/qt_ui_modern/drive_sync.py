"""Built-in Drive sync — runs in main app thread, watches output folder, uploads to Drive.

Reads config from ~/.veo_pipeline/onboarded.json (set during onboarding wizard):
  - output_dir: local watch folder
  - drive_id: Google Drive folder ID
  - tg_bot, tg_chat: Telegram notify (optional)

Auto-disabled if drive_id missing.
"""
from __future__ import annotations
import os
import json
import time
import re
import hashlib
import threading
from pathlib import Path
from datetime import datetime

ONBOARD_FILE = Path.home() / ".veo_pipeline" / "onboarded.json"
PROCESSED_DB = Path.home() / ".veo_pipeline" / "drive_processed.json"
CRED_FILE = Path.home() / ".veo_pipeline" / "drive_credentials.json"


def load_config() -> dict:
    if ONBOARD_FILE.exists():
        try:
            return json.loads(ONBOARD_FILE.read_text())
        except Exception:
            pass
    return {}


def is_enabled() -> bool:
    cfg = load_config()
    return bool(cfg.get("drive_id")) and CRED_FILE.exists()


def _file_hash(p: Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _load_db() -> dict:
    if PROCESSED_DB.exists():
        try: return json.loads(PROCESSED_DB.read_text())
        except: pass
    return {}


def _save_db(d: dict):
    PROCESSED_DB.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DB.write_text(json.dumps(d, indent=2))


def _derive_topic(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"\b\d{8,}\b", "", stem)
    stem = re.sub(r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b", "", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem[:50] or "untitled"


def _rename(p: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    new_name = f"{ts}_{_derive_topic(p.name)}.mp4"
    new_path = p.parent / new_name
    if new_path.exists():
        new_name = f"{ts}_{_derive_topic(p.name)}_{_file_hash(p)[:6]}.mp4"
        new_path = p.parent / new_name
    p.rename(new_path)
    return new_path


def _drive_upload(p: Path, folder_id: str) -> str | None:
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("[drive] google-api-python-client missing")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(
            str(CRED_FILE), scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        media = MediaFileUpload(str(p), mimetype="video/mp4", resumable=True)
        meta = {"name": p.name, "parents": [folder_id]}
        f = svc.files().create(body=meta, media_body=media, fields="id,name").execute()
        print(f"[drive] uploaded {p.name} → {f['id']}")
        return f["id"]
    except Exception as e:
        print(f"[drive] upload failed: {e}")
        return None


def _tg_notify(msg: str, cfg: dict):
    bot = cfg.get("tg_bot", "")
    chat = cfg.get("tg_chat", "")
    if not bot or not chat:
        return
    try:
        import urllib.request
        import json as _json
        url = f"https://api.telegram.org/bot{bot}/sendMessage"
        data = _json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass


def _process(p: Path, cfg: dict):
    if not p.exists() or p.stat().st_size < 100_000:
        return
    # Wait file size stable
    last = -1
    for _ in range(60):
        sz = p.stat().st_size
        if sz == last and sz > 100_000:
            break
        last = sz
        time.sleep(2)

    h = _file_hash(p)
    db = _load_db()
    if h in db:
        return

    new_p = _rename(p)
    folder_id = cfg.get("drive_id", "")
    drive_id = _drive_upload(new_p, folder_id) if folder_id else None

    db[h] = {
        "original": p.name,
        "renamed": new_p.name,
        "size_mb": round(new_p.stat().st_size / 1024 / 1024, 1),
        "drive_id": drive_id,
        "ts": datetime.now().isoformat(),
    }
    _save_db(db)

    msg = f"🎬 <b>Video ready</b>\nFile: <code>{new_p.name}</code>\nSize: {db[h]['size_mb']}MB\n"
    msg += f"Drive: <code>{drive_id}</code>" if drive_id else "Drive: skipped"
    _tg_notify(msg, cfg)


def _watch_loop():
    """Polling watcher (no watchdog dep — uses os.listdir + mtime tracking)."""
    cfg = load_config()
    watch_dir = Path(cfg.get("output_dir", "")) if cfg.get("output_dir") else None
    if not watch_dir or not watch_dir.exists():
        print(f"[drive] output_dir not set or missing")
        return

    print(f"[drive] watching {watch_dir} → folder {cfg.get('drive_id','')[:20]}...")

    seen = set()
    # Process existing files first
    for p in watch_dir.glob("*.mp4"):
        seen.add(p.name)
        try: _process(p, cfg)
        except Exception as e: print(f"[drive] {e}")

    while True:
        try:
            time.sleep(10)
            # Reload config periodically (user may change in Settings)
            cfg = load_config()
            current = {p.name for p in watch_dir.glob("*.mp4")}
            new_files = current - seen
            for fname in new_files:
                p = watch_dir / fname
                seen.add(fname)
                time.sleep(3)  # let file finish writing
                try: _process(p, cfg)
                except Exception as e: print(f"[drive] {e}")
        except Exception as e:
            print(f"[drive] loop error: {e}")
            time.sleep(30)


def start_background():
    """Start Drive sync watcher in background daemon thread."""
    if not is_enabled():
        print("[drive] disabled (no drive_id or credentials)")
        return None
    t = threading.Thread(target=_watch_loop, daemon=True, name="DriveSync")
    t.start()
    return t
