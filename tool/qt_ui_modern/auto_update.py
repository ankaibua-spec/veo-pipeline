"""Self-updater for VEO Pipeline Pro .exe build (hardened).

Flow:
1. On startup, check GitHub Releases API for latest tag
2. Compare with bundled APP_VERSION
3. If newer: download zip from release asset
4. Verify SHA-256 against checksum embedded in release body (if present)
5. Extract to randomised temp folder (no fixed path TOCTOU)
6. Write a swap script that reads paths from a sibling text file (no f-string
   into cmd grammar — paths cannot inject shell)
7. Wait for current exe to exit using a marker file, not raw PID
8. robocopy /MIR — with sentinel file in source so empty extract aborts
9. Trigger app restart
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import zipfile
import urllib.request
from pathlib import Path
from . import theme as t

GITHUB_API = "https://api.github.com/repos/ankaibua-spec/veo-pipeline/releases/latest"
ASSET_NAME = "VEO_Pipeline_Pro_Windows.zip"

# Pattern in release body: line `SHA256: <hex>` or `sha256: <hex>` (any case).
SHA256_RE = re.compile(r"(?im)^\s*sha-?256\s*[:=]\s*([0-9a-f]{64})\s*$")


def _is_frozen() -> bool:
    """True if running from PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def _exe_dir() -> Path:
    """Folder containing VEO_Pipeline_Pro.exe (onedir bundle root)."""
    return Path(sys.executable).resolve().parent if _is_frozen() else Path(__file__).parent.parent


def _parse_version(s: str) -> tuple[int, ...]:
    s = s.strip().lstrip("v")
    parts = []
    for chunk in s.split("."):
        try: parts.append(int(chunk.split("-")[0]))
        except Exception: break
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


def _expected_sha256(release: dict) -> str | None:
    body = release.get("body", "") or ""
    m = SHA256_RE.search(body)
    return m.group(1).lower() if m else None


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_update(release: dict, progress_cb=None) -> Path | None:
    """Download zip to temp. Returns local zip path or None on failure / hash mismatch."""
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
    except Exception as e:
        print(f"[update] download fail: {e}")
        return None

    # Optional integrity check — if release body has `SHA256: <hex>` line, enforce.
    expected = _expected_sha256(release)
    if expected:
        actual = _file_sha256(tmp)
        if actual.lower() != expected:
            print(f"[update] SHA256 mismatch: expected {expected[:16]}... got {actual[:16]}...")
            try: tmp.unlink()
            except Exception: pass
            return None
        print(f"[update] SHA256 verified: {actual[:16]}...")
    else:
        print("[update] WARNING: release body has no SHA256 — integrity unchecked")

    return tmp


def _safe_extract(zf: zipfile.ZipFile, dest: Path):
    """Extract with strict zip-slip protection.

    Uses os.path.commonpath instead of str.startswith to avoid the
    `dest=foo` vs `foo_pwn/x` sibling-prefix bypass.
    """
    dest_resolved = str(dest.resolve())
    for member in zf.namelist():
        # Reject absolute paths and drive letters outright
        if member.startswith(("/", "\\")) or (len(member) >= 2 and member[1] == ":"):
            raise ValueError(f"absolute path in zip: {member}")
        # Reject parent traversal in raw member name
        norm = os.path.normpath(member)
        if norm.startswith(".." + os.sep) or norm == "..":
            raise ValueError(f"parent traversal in zip: {member}")
        target = (dest / member).resolve()
        target_str = str(target)
        try:
            common = os.path.commonpath([dest_resolved, target_str])
        except ValueError:
            raise ValueError(f"path mismatch (different drives?): {member}")
        if common != dest_resolved:
            raise ValueError(f"zip-slip detected: {member}")
    zf.extractall(dest)


# Filename component validators — defence-in-depth for paths going into .bat.
_SAFE_DIR_RE = re.compile(r"^[A-Za-z]:[\\/][^\x00\"<>|*?]+$")
_SAFE_BARE_RE = re.compile(r"^[^\x00\"<>|*?]+$")


def _validate_path(p: Path, label: str) -> str:
    """Reject paths containing shell metachars or NUL. Return resolved string."""
    s = str(p.resolve())
    if any(c in s for c in ('"', '\x00', '\r', '\n')):
        raise ValueError(f"{label} contains forbidden char: {s!r}")
    return s


def apply_update(zip_path: Path):
    """Extract update + write swap script + spawn it + exit current process.

    Hardening vs v1:
    - Randomised extract dir (anti-TOCTOU, no fixed `%TEMP%/veo_update_extract`)
    - Marker-file readiness check (sentinel inside extract; .bat aborts if missing
      so an empty / partial extract never nukes the install)
    - Paths written to a side-car file that the .bat reads via `set /p` —
      no f-string interpolation of user-controlled strings into cmd grammar
    - Exit-marker file replaces raw PID wait (no PID-reuse race)
    - Robocopy errorlevel checked properly + rollback on >=8 only
    """
    if not _is_frozen():
        print("[update] dev mode — skipping apply")
        return False

    target_dir = _exe_dir()
    # Randomised, per-run extract dir — kills the fixed-path TOCTOU window.
    nonce = secrets.token_hex(8)
    work_dir = Path(tempfile.gettempdir()) / f"veo_update_{nonce}"
    extract_dir = work_dir / "payload"
    work_dir.mkdir(parents=True, exist_ok=False)
    extract_dir.mkdir()

    try:
        with zipfile.ZipFile(zip_path) as zf:
            _safe_extract(zf, extract_dir)
    except Exception as e:
        print(f"[update] extract fail: {e}")
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    # Sentinel proves extract completed — .bat refuses to mirror an empty/partial dir.
    sentinel = extract_dir / ".veo_update_ready"
    sentinel.write_bytes(b"ok")

    # Sanity-check: VEO_Pipeline_Pro.exe must exist in the extracted payload.
    if not (extract_dir / "VEO_Pipeline_Pro.exe").exists():
        print("[update] payload missing VEO_Pipeline_Pro.exe — abort")
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    exe_path = target_dir / "VEO_Pipeline_Pro.exe"
    backup_dir = Path(str(target_dir) + "_backup")
    exit_marker = work_dir / "exit_marker"   # current process touches before _exit

    # Validate every path that lands in the swap script. Defence against unexpected
    # username/temp-dir edge cases. shlex.quote isn't valid for cmd.exe; we keep
    # paths in a side-car file and let the script read them as data.
    paths_file = work_dir / "paths.txt"
    paths_file.write_text(
        "\n".join([
            _validate_path(target_dir,  "target_dir"),
            _validate_path(backup_dir,  "backup_dir"),
            _validate_path(extract_dir, "extract_dir"),
            _validate_path(exe_path,    "exe_path"),
            _validate_path(work_dir,    "work_dir"),
            _validate_path(exit_marker, "exit_marker"),
        ]),
        encoding="utf-8",
    )

    # Bat lives OUTSIDE work_dir so the bat itself doesn't lock the dir we
    # want to clean up. Self-delete via `del "%~f0"` still works.
    bat_path = Path(tempfile.gettempdir()) / f"veo_swap_{nonce}.bat"
    # Note: the .bat below contains NO f-string interpolation of user-controlled
    # paths. The only interpolated value is `paths_file`, which is a path the
    # updater itself just wrote and validated. Paths read via `set /p` are
    # treated as data, never as command tokens.
    bat_path.write_text(
        "@echo off\r\n"
        "setlocal enabledelayedexpansion\r\n"
        "\r\n"
        "REM Read paths written by the updater (one per line).\r\n"
        "set /p TARGET=<\"" + str(paths_file) + "\"\r\n"
        "for /f \"usebackq skip=1 delims=\" %%I in (\"" + str(paths_file) + "\") do (\r\n"
        "  if not defined BACKUP   ( set \"BACKUP=%%I\"   ) else (\r\n"
        "  if not defined EXTRACT  ( set \"EXTRACT=%%I\"  ) else (\r\n"
        "  if not defined EXEPATH  ( set \"EXEPATH=%%I\"  ) else (\r\n"
        "  if not defined WORKDIR  ( set \"WORKDIR=%%I\"  ) else (\r\n"
        "  if not defined EXITFLAG ( set \"EXITFLAG=%%I\" )))))\r\n"
        ")\r\n"
        "\r\n"
        "REM Wait for the running app to drop the exit-marker file (max 60s).\r\n"
        "set /a counter=0\r\n"
        ":waitloop\r\n"
        "set /a counter+=1\r\n"
        "if %counter% gtr 60 goto :proceed\r\n"
        "if not exist \"!EXITFLAG!\" (\r\n"
        "    timeout /t 1 /nobreak >NUL\r\n"
        "    goto waitloop\r\n"
        ")\r\n"
        ":proceed\r\n"
        "\r\n"
        "REM Refuse to mirror if the readiness sentinel is missing.\r\n"
        "if not exist \"!EXTRACT!\\.veo_update_ready\" (\r\n"
        "    echo [update] sentinel missing - abort\r\n"
        "    goto cleanup\r\n"
        ")\r\n"
        "\r\n"
        "REM Clean any old backup before snapshotting.\r\n"
        "if exist \"!BACKUP!\" rmdir /S /Q \"!BACKUP!\" >NUL 2>&1\r\n"
        "\r\n"
        "robocopy \"!TARGET!\" \"!BACKUP!\" /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS >NUL\r\n"
        "if errorlevel 8 (\r\n"
        "    echo [update] backup failed - abort, install untouched\r\n"
        "    goto cleanup\r\n"
        ")\r\n"
        "\r\n"
        "robocopy \"!EXTRACT!\" \"!TARGET!\" /MIR /XF .veo_update_ready /R:2 /W:2 /NFL /NDL /NJH /NJS >NUL\r\n"
        "if errorlevel 8 (\r\n"
        "    robocopy \"!BACKUP!\" \"!TARGET!\" /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS >NUL\r\n"
        "    start \"\" \"!EXEPATH!\"\r\n"
        "    goto cleanup\r\n"
        ")\r\n"
        "\r\n"
        "start \"\" \"!EXEPATH!\"\r\n"
        "\r\n"
        ":cleanup\r\n"
        "rmdir /S /Q \"!BACKUP!\"  >NUL 2>&1\r\n"
        "rmdir /S /Q \"!WORKDIR!\" >NUL 2>&1\r\n"
        "del \"%~f0\" >NUL 2>&1\r\n"
        "exit /b 0\r\n",
        encoding="ascii",
    )

    # NB: exit_marker is NOT created here. The .bat polls `if exist EXITFLAG`,
    # so the file must come into existence only when the launcher calls
    # signal_exit() right before os._exit(). Pre-creating the file would make
    # the .bat skip its wait loop and start robocopy while the .exe is still
    # holding file locks → robocopy errorlevel 8 → rollback → no swap.

    # Spawn detached.
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat_path)],
        creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        close_fds=True,
    )
    # Tell the caller where the exit marker lives so launcher_pro can finalise it.
    return {"exit_marker": str(exit_marker), "work_dir": str(work_dir)}


def signal_exit(handle) -> None:
    """Caller invokes right before os._exit(0). Writes the .bat unblock flag."""
    if not handle:
        return
    try:
        Path(handle["exit_marker"]).write_text("exit\n", encoding="ascii")
    except Exception as e:
        print(f"[update] signal_exit fail: {e}")


def check_and_prompt(parent_window) -> bool:
    """Sync check + prompt + apply. Returns True if update started (caller should exit app)."""
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
        QMessageBox.warning(parent_window, "Update failed",
            "Download or integrity check failed. Try again later.")
        return False

    handle = apply_update(zip_path)
    if handle:
        # Stash for launcher_pro so it can call signal_exit() right before _exit.
        global _LAST_HANDLE
        _LAST_HANDLE = handle
        QMessageBox.information(parent_window, "Updating",
            "App will close + restart with new version.")
        return True
    else:
        QMessageBox.warning(parent_window, "Update failed", "Could not apply update.")
        return False


_LAST_HANDLE: dict | None = None


def consume_exit_handle() -> dict | None:
    """Launcher calls this just before os._exit() to grab the marker info."""
    global _LAST_HANDLE
    h = _LAST_HANDLE
    _LAST_HANDLE = None
    return h
