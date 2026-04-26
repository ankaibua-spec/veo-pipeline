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


def restart_post_processor():
    """Kill existing post_processor + relaunch."""
    if sys.platform == "win32":
        run("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq post_processor*\"")
    else:
        run("pkill -f post_processor.py")
    time.sleep(2)
    pp = REPO_DIR / "pc" / "post_processor.py"
    if pp.exists():
        if sys.platform == "win32":
            subprocess.Popen(["pythonw", str(pp)], creationflags=0x08000000)
        else:
            subprocess.Popen(["python3", str(pp)], start_new_session=True)
        log("post_processor restarted")


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
    log("pull done; restarting post_processor")
    restart_post_processor()

    STATE_FILE.write_text(json.dumps({
        "last_update": int(time.time()),
        "from": local, "to": remote_sha, "msg": remote_msg
    }, indent=2))
    log("✅ updated")


if __name__ == "__main__":
    main()
