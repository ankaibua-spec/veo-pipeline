"""Self-updater for VEO Pipeline Pro .exe build.

Flow:
1. On startup, check GitHub Releases API for latest tag
2. Compare with bundled APP_VERSION
3. If newer: download zip from release asset
4. Extract to temp folder, write batch script
5. Batch script: wait for current exe to exit → swap files → relaunch
6. Trigger app restart
"""
from __future__ import annotations
import json
import os
import sys
import shutil
import tempfile
import zipfile
import subprocess
import urllib.request
from pathlib import Path
from . import theme as t

GITHUB_API = "https://api.github.com/repos/ankaibua-spec/veo-pipeline/releases/latest"
ASSET_NAME = "VEO_Pipeline_Pro_Windows.zip"


def _is_frozen() -> bool:
    """True if running from PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def _exe_dir() -> Path:
    """Folder containing VEO_Pipeline_Pro.exe (onedir bundle root)."""
    return Path(sys.executable).resolve().parent if _is_frozen() else Path(__file__).parent.parent


def _parse_version(s: str) -> tuple[int, ...]:
    """`v5.0.1` or `5.0.1` → (5,0,1). Always 3-tuple normalized for compare."""
    s = s.strip().lstrip("v")
    parts = []
    for chunk in s.split("."):
        try: parts.append(int(chunk.split("-")[0]))
        except Exception: break
    # Pad to 3 elements so (5,0) compares as (5,0,0) vs (5,0,1)
    while len(parts) < 3: parts.append(0)
    return tuple(parts[:3])


def check_latest() -> dict | None:
    """Returns release dict if newer version, else None."""
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "veo-updater"})
        with urllib.request.urlopen(req, timeout=8) as r:
            release = json.loads(r.read().decode())
        latest = _parse_version(release.get("tag_name", "0"))
        current = _parse_version(t.APP_VERSION)
        if latest <= current:
            return None
        return release
    except Exception as e:
        print(f"[update] check fail: {e}")
        return None


def _find_zip_asset(release: dict) -> str | None:
    for asset in release.get("assets", []):
        if asset.get("name") == ASSET_NAME:
            return asset.get("browser_download_url")
    return None


def download_update(release: dict, progress_cb=None) -> Path | None:
    """Download zip to temp. Returns local zip path or None."""
    url = _find_zip_asset(release)
    if not url:
        return None
    tmp = Path(tempfile.gettempdir()) / f"veo_update_{release.get('tag_name','x')}.zip"
    try:
        with urllib.request.urlopen(url, timeout=120) as src, open(tmp, "wb") as dst:
            total = int(src.headers.get("Content-Length", 0))
            done = 0
            chunk = 256 * 1024
            while True:
                buf = src.read(chunk)
                if not buf: break
                dst.write(buf)
                done += len(buf)
                if progress_cb and total:
                    progress_cb(done, total)
        return tmp
    except Exception as e:
        print(f"[update] download fail: {e}")
        return None


def _safe_extract(zf: zipfile.ZipFile, dest: Path):
    """Extract zip with zip-slip protection. Reject paths escaping dest."""
    dest_resolved = dest.resolve()
    for member in zf.namelist():
        target = (dest / member).resolve()
        if not str(target).startswith(str(dest_resolved)):
            raise ValueError(f"zip-slip detected: {member}")
    zf.extractall(dest)


def apply_update(zip_path: Path):
    """Extract update + write batch script + spawn it + exit current process.

    Improvements over v1:
    - robocopy /MIR removes stale files in old install
    - tasklist /FI exact PID match (no substring race)
    - zip-slip protection on extract
    - rollback from backup if swap fails
    - cleanup old backup before new one
    """
    if not _is_frozen():
        print("[update] dev mode — skipping apply")
        return False

    target_dir = _exe_dir()
    extract_dir = Path(tempfile.gettempdir()) / "veo_update_extract"
    if extract_dir.exists(): shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir(parents=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            _safe_extract(zf, extract_dir)
    except Exception as e:
        print(f"[update] extract fail: {e}")
        return False

    pid = os.getpid()
    bat = Path(tempfile.gettempdir()) / "veo_swap.bat"
    exe_path = target_dir / "VEO_Pipeline_Pro.exe"
    backup_dir = Path(str(target_dir) + "_backup")

    # robocopy exit codes 0-7 = success; 8+ = failure
    bat.write_text(f"""@echo off
setlocal enabledelayedexpansion

REM Wait for current process to exit (exact PID match)
:waitloop
tasklist /FI "PID eq {pid}" /NH 2>NUL | find /I "VEO_Pipeline_Pro" >NUL
if "%errorlevel%"=="0" (
    timeout /t 1 /nobreak >NUL
    goto waitloop
)

REM Remove old backup
if exist "{backup_dir}" rmdir /S /Q "{backup_dir}" >NUL 2>&1

REM Mirror current to backup (full snapshot)
robocopy "{target_dir}" "{backup_dir}" /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS >NUL

REM Mirror new build over current (removes stale files from old version)
robocopy "{extract_dir}" "{target_dir}" /MIR /R:2 /W:2 /NFL /NDL /NJH /NJS >NUL
if errorlevel 8 (
    REM Failure — rollback from backup
    robocopy "{backup_dir}" "{target_dir}" /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS >NUL
    start "" "{exe_path}"
    rmdir /S /Q "{extract_dir}" >NUL 2>&1
    del "%~f0"
    exit /b 1
)

REM Success — relaunch
start "" "{exe_path}"

REM Cleanup
rmdir /S /Q "{extract_dir}" >NUL 2>&1
rmdir /S /Q "{backup_dir}" >NUL 2>&1
del "%~f0"
""", encoding="ascii")

    # Spawn detached
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat)],
        creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        close_fds=True,
    )
    return True


def check_and_prompt(parent_window) -> bool:
    """Synchronous check + prompt + apply. Called from main thread on startup.
    Returns True if update started (caller should exit app)."""
    release = check_latest()
    if not release:
        return False

    from PyQt6.QtWidgets import QMessageBox
    tag = release.get("tag_name", "?")
    notes = (release.get("body", "") or "")[:500]
    msg = QMessageBox(parent_window)
    msg.setWindowTitle(f"{t.APP_NAME} — Update Available")
    msg.setText(f"<b>New version {tag}</b> available.\n\nCurrent: {t.APP_VERSION}")
    if notes:
        msg.setDetailedText(notes)
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    msg.button(QMessageBox.StandardButton.Yes).setText("Update Now")
    msg.button(QMessageBox.StandardButton.No).setText("Later")

    if msg.exec() != QMessageBox.StandardButton.Yes:
        return False

    # Show download progress
    from PyQt6.QtWidgets import QProgressDialog
    pd = QProgressDialog("Downloading update...", "Cancel", 0, 100, parent_window)
    pd.setWindowTitle(f"{t.APP_NAME} — Updating")
    pd.setMinimumDuration(0)
    pd.setValue(0)
    pd.show()

    def on_progress(done, total):
        pct = int(done * 100 / total) if total else 0
        pd.setValue(pct)
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

    zip_path = download_update(release, progress_cb=on_progress)
    pd.close()
    if not zip_path:
        QMessageBox.warning(parent_window, "Update failed", "Download failed. Try again later.")
        return False

    if apply_update(zip_path):
        QMessageBox.information(parent_window, "Updating", "App will close + restart with new version.")
        return True
    else:
        QMessageBox.warning(parent_window, "Update failed", "Could not apply update.")
        return False
