"""
Auto-updater PC side.
Pulls latest from GitHub via git, restarts post_processor.
Run periodically via Task Scheduler or manually.

Usage:
  python updater.py            # check + update if newer
  python updater.py --check    # check only, no install
  python updater.py --force    # force pull even if same commit
"""
from __future__ import annotations
import os, sys, subprocess, json, urllib.request, hashlib, time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent  # repo root
GITHUB_API = "https://api.github.com/repos/ankaibua-spec/veo-pipeline/commits/main"
STATE_FILE = REPO_DIR / "pc" / ".updater_state.json"


def log(msg: str):
    print(f"[updater] {msg}")


def run(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=False, capture_output=True, text=True, **kw)


def git_local_commit() -> str | None:
    r = run(["git", "rev-parse", "HEAD"], cwd=REPO_DIR)
    if r.returncode == 0:
        return r.stdout.strip()
    return None


def github_latest_commit() -> dict | None:
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "veo-updater"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"github fetch fail: {e}")
        return None


def git_pull() -> tuple[bool, str]:
    r = run(["git", "pull", "--rebase", "--autostash"], cwd=REPO_DIR)
    return r.returncode == 0, (r.stdout + r.stderr)[-2000:]


def write_restart_marker():
    """Write marker file. post_processor checks marker on next iteration and self-exits.
    External wrapper script (or Task Scheduler trigger) re-launches.
    Avoids race when updater is invoked from inside post_processor's own thread.
    """
    marker = REPO_DIR / "pc" / ".restart_required"
    marker.write_text(f"{int(time.time())}\n")
    log(f"restart marker written: {marker}")
    log("post_processor will exit on next idle tick; relaunch via wrapper/Task Scheduler")


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    force = "--force" in args

    local = git_local_commit()
    if not local:
        log("not a git repo; skipping")
        return

    remote = github_latest_commit()
    if not remote:
        return

    remote_sha = remote.get("sha", "")
    remote_msg = remote.get("commit", {}).get("message", "").splitlines()[0][:80]

    log(f"local : {local[:8]}")
    log(f"remote: {remote_sha[:8]} - {remote_msg}")

    if local == remote_sha and not force:
        log("up to date")
        return

    if check_only:
        log("update available (use --force or omit --check to install)")
        return

    log("pulling...")
    ok, out = git_pull()
    if not ok:
        log(f"pull failed:\n{out}")
        return
    log("pull done; signaling post_processor to restart")
    write_restart_marker()

    STATE_FILE.write_text(json.dumps({
        "last_update": int(time.time()),
        "from": local, "to": remote_sha, "msg": remote_msg
    }, indent=2))
    log("✅ updated")


if __name__ == "__main__":
    main()
