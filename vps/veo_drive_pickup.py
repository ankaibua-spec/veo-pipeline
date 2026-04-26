#!/usr/bin/env python3
"""
VPS-side pickup: poll Drive folder, download new videos, queue YouTube upload.
Cron: */5 * * * * python3 /root/veo_drive_pickup.py

Reads:
  - VEO_DRIVE_FOLDER_ID env or config
  - Drive service account at /root/.veo_drive_creds.json

Writes:
  - /opt/english-pronunciation/storage/veo_pickup/<filename>.mp4
  - SQLite: /opt/english-pronunciation/storage/database.db table veo_drive_files
  - Telegram channel Video Veo3 (-1003375527350)
"""
from __future__ import annotations
import os, sys, json, re, sqlite3, subprocess, time
from pathlib import Path
from datetime import datetime
import urllib.request

CRED_FILE = "/root/.veo_drive_creds.json"
DRIVE_FOLDER_ID = os.environ.get("VEO_DRIVE_FOLDER_ID", "")
PICKUP_DIR = Path("/opt/english-pronunciation/storage/veo_pickup")
DB_PATH = "/opt/english-pronunciation/storage/database.db"
TG_BOT = os.environ.get("VEO_TG_BOT", "")
TG_CHAT = os.environ.get("VEO_TG_CHAT", "")
LOCK = "/tmp/veo_drive_pickup.lock"

PICKUP_DIR.mkdir(parents=True, exist_ok=True)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import io
except ImportError:
    print("Install: pip3 install google-api-python-client google-auth")
    sys.exit(1)


def log(msg):
    print(f"[{datetime.now().strftime('%F %T')}] {msg}")


def tg_notify(msg):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
        data = json.dumps({"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        log(f"tg fail: {e}")


def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS veo_drive_files (
            drive_id TEXT PRIMARY KEY,
            filename TEXT,
            topic TEXT,
            size INTEGER,
            local_path TEXT,
            downloaded_at DATETIME,
            uploaded_at DATETIME,
            youtube_url TEXT,
            status TEXT DEFAULT 'new'
        )
    """)
    c.commit()
    c.close()


def drive_svc():
    creds = service_account.Credentials.from_service_account_file(
        CRED_FILE, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_drive_files():
    svc = drive_svc()
    q = f"'{DRIVE_FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false"
    res = svc.files().list(q=q, fields="files(id,name,size,modifiedTime)", pageSize=200).execute()
    return res.get("files", [])


def parse_topic(filename: str) -> str:
    """Filename: YYYY-MM-DD_HH-MM_<topic>.mp4"""
    m = re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_(.+?)\.mp4$", filename)
    return m.group(1).replace("_", " ").replace("-", " ") if m else Path(filename).stem


def download_drive(file_id, dest: Path):
    svc = drive_svc()
    req = svc.files().get_media(fileId=file_id)
    fh = io.FileIO(str(dest), "wb")
    dl = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    fh.close()


def main():
    if not DRIVE_FOLDER_ID:
        log("VEO_DRIVE_FOLDER_ID not set; aborting")
        return

    # Lock via fcntl (atomic, no TOCTOU)
    import fcntl
    lock_fd = open(LOCK, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another instance running; skip")
        lock_fd.close()
        return
    lock_fd.write(str(os.getpid()))
    lock_fd.flush()

    c = None
    try:
        init_db()
        files = list_drive_files()
        log(f"Drive folder has {len(files)} videos")
        c = sqlite3.connect(DB_PATH)

        new_count = 0
        for f in files:
            fid = f["id"]
            name = f["name"]
            size = int(f.get("size", 0))

            row = c.execute("SELECT status FROM veo_drive_files WHERE drive_id=?", (fid,)).fetchone()
            if row and row[0] not in ("new", "error"):
                continue

            local = PICKUP_DIR / name
            log(f"download {name} ({size//1024//1024}MB)")

            # Retry up to 3x with backoff
            ok = False
            err_msg = ""
            for attempt in range(3):
                try:
                    download_drive(fid, local)
                    ok = True
                    break
                except Exception as e:
                    err_msg = str(e)
                    log(f"  attempt {attempt+1} failed: {e}")
                    time.sleep(5 * (attempt + 1))

            if not ok:
                c.execute("""
                    INSERT OR REPLACE INTO veo_drive_files
                    (drive_id, filename, size, status)
                    VALUES (?, ?, ?, 'error')
                """, (fid, name, size))
                c.commit()
                continue

            topic = parse_topic(name)
            c.execute("""
                INSERT OR REPLACE INTO veo_drive_files
                (drive_id, filename, topic, size, local_path, downloaded_at, status)
                VALUES (?, ?, ?, ?, ?, datetime('now'), 'downloaded')
            """, (fid, name, topic, size, str(local)))
            c.commit()
            new_count += 1

            tg_notify(
                f"📥 <b>VEO video picked up</b>\n"
                f"File: <code>{name}</code>\n"
                f"Topic: {topic}\n"
                f"Size: {size//1024//1024}MB\n"
                f"Status: queued for YouTube upload"
            )

        log(f"new={new_count}")

    finally:
        if c: c.close()
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            os.unlink(LOCK)
        except Exception: pass


if __name__ == "__main__":
    main()
