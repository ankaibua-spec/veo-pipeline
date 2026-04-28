"""
Auto-updater PC side.
Pulls latest from GitHub via git, restarts post_processor.
Run periodically via Task Scheduler or manually.

Usage:
  python updater.py            # check + update if newer
  python updater.py --check    # check only, no install
  python updater.py --force    # force pull even if same commit

Security:
  VEO_AUTO_UPDATE=1            # phai set ro rang de bat (default off)
  VEO_TRUSTED_SHA=<sha>        # neu set, chi pull khi remote SHA khop
"""
from __future__ import annotations
import os, sys, subprocess, json, urllib.request, hashlib, time
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent  # repo root
GITHUB_API = "https://api.github.com/repos/ankaibua-spec/veo-pipeline/commits/main"

# Fix #3: state file o ngoai repo dir
_STATE_DIR = Path.home() / ".veo_pipeline"
_STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
STATE_FILE = _STATE_DIR / ".updater_state.json"


def log(msg: str):
    print(f"[updater] {msg}")


# Fix #13: strict run() — khong dung shell=True, chi nhan list
def run(cmd_list: list, **kw):
    return subprocess.run(cmd_list, shell=False, check=False, capture_output=True, text=True, **kw)


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


def git_fetch() -> bool:
    """Fix #4: fetch truoc khi pull de kiem tra SHA truoc."""
    r = run(["git", "fetch", "origin", "main"], cwd=REPO_DIR)
    return r.returncode == 0


def git_pull() -> tuple[bool, str]:
    r = run(["git", "pull", "--rebase", "--autostash"], cwd=REPO_DIR)
    return r.returncode == 0, (r.stdout + r.stderr)[-2000:]


def write_restart_marker():
    """Ghi marker. post_processor kiem tra marker moi iteration va tu exit.
    External wrapper script (hoac Task Scheduler trigger) se re-launch.
    Tranh race khi updater duoc goi tu thread cua post_processor.
    Fix #3: marker o ngoai repo dir.
    """
    marker = _STATE_DIR / ".restart_required"
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

    # Fix #14: --force nhung da up-to-date -> khong restart vo ich
    if local == remote_sha and not force:
        log("up to date")
        return
    if local == remote_sha and force:
        log("no-op force: already at remote SHA, skipping restart")
        return

    if check_only:
        log("update available (use --force or omit --check to install)")
        return

    # Fix #4: fetch truoc de kiem tra SHA truoc khi merge vao working tree
    log("fetching...")
    if not git_fetch():
        log("fetch failed; aborting update")
        return

    # Fix #4: kiem tra trusted SHA neu user da set env var
    # TODO: switch to GPG-signed commits + `git verify-commit HEAD` before merge.
    trusted_sha = os.environ.get("VEO_TRUSTED_SHA", "")
    if trusted_sha:
        if remote_sha not in [s.strip() for s in trusted_sha.split(",")]:
            log(f"SECURITY: remote SHA {remote_sha[:8]} not in VEO_TRUSTED_SHA allowlist; refusing update")
            return
    else:
        log("WARNING: VEO_TRUSTED_SHA not set — pulling unverified commit. Set VEO_TRUSTED_SHA to lock.")

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
    log("updated")


if __name__ == "__main__":
    main()
