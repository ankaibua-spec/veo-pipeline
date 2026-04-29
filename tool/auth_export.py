"""Export/Import login state — portable JSON via Playwright storage_state.

Storage state JSON includes: cookies (HttpOnly, Secure, SameSite), origins
(localStorage + IndexedDB token), but NOT sessionStorage (per-tab).
DPAPI-encrypted Chrome cookies decrypted by Playwright at export time.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from settings_manager import CHROME_USER_DATA_ROOT, DATA_GENERAL_DIR


def _login_states_dir() -> Path:
    d = DATA_GENERAL_DIR / "login_states"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_export_path(profile_name: str) -> Path:
    safe = "".join(c for c in profile_name if c.isalnum() or c in "_-")
    ts = time.strftime("%Y%m%d_%H%M%S")
    return _login_states_dir() / f"{safe}_{ts}.json"


def export_login_state(
    profile_name: str,
    out_path: "str | Path",
    chrome_root: "Path | None" = None,
    log_callback=None,
) -> dict:
    """Dump cookies + origins to JSON. Returns {'cookies': N, 'origins': M, 'path': str}.

    Chrome must NOT be running with the same profile (Playwright will fail to
    acquire lock). Caller responsibility to close Chrome first.
    """
    log = log_callback or (lambda m: None)
    chrome_root = chrome_root or CHROME_USER_DATA_ROOT
    user_data = Path(chrome_root) / profile_name
    if not user_data.exists():
        raise FileNotFoundError(f"Profile not found: {user_data}")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        log(f"Launching Chromium with profile: {profile_name}")
        ctx = p.chromium.launch_persistent_context(
            str(user_data),
            headless=True,
            channel="chrome",
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        try:
            state = ctx.storage_state()
            ctx.close()
        except Exception:
            try:
                ctx.close()
            except Exception:
                pass
            raise

    out_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    n_cookies = len(state.get("cookies", []))
    n_origins = len(state.get("origins", []))
    log(f"Exported {n_cookies} cookies, {n_origins} origins -> {out_path}")
    return {"cookies": n_cookies, "origins": n_origins, "path": str(out_path)}


def import_login_state(
    profile_name: str,
    in_path: "str | Path",
    chrome_root: "Path | None" = None,
    log_callback=None,
) -> dict:
    """Inject saved state into profile. Profile created if missing.

    Strategy: launch persistent context with storage_state arg -> Playwright
    seeds cookies + localStorage into the profile. Chrome must NOT be running
    with the same profile.
    """
    log = log_callback or (lambda m: None)
    chrome_root = chrome_root or CHROME_USER_DATA_ROOT
    user_data = Path(chrome_root) / profile_name
    user_data.mkdir(parents=True, exist_ok=True)
    in_path = Path(in_path)
    if not in_path.exists():
        raise FileNotFoundError(f"State file not found: {in_path}")
    state = json.loads(in_path.read_text(encoding="utf-8"))
    n_cookies = len(state.get("cookies", []))
    n_origins = len(state.get("origins", []))

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        log(f"Seeding profile {profile_name} with {n_cookies} cookies, {n_origins} origins")
        ctx = p.chromium.launch_persistent_context(
            str(user_data),
            headless=True,
            channel="chrome",
            storage_state=str(in_path),
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        try:
            # storage_state arg seeds at context creation. Open about:blank to
            # force write to profile disk.
            page = ctx.new_page()
            page.goto("about:blank")
            ctx.close()
        except Exception:
            try:
                ctx.close()
            except Exception:
                pass
            raise
    log(f"Imported state to profile {profile_name}")
    return {"cookies": n_cookies, "origins": n_origins, "profile": profile_name}


def list_saved_states() -> list:
    """List all saved JSON files in login_states/."""
    d = _login_states_dir()
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            st = json.loads(f.read_text(encoding="utf-8"))
            out.append(
                {
                    "path": str(f),
                    "name": f.stem,
                    "size": f.stat().st_size,
                    "mtime": f.stat().st_mtime,
                    "cookies": len(st.get("cookies", [])),
                    "origins": len(st.get("origins", [])),
                }
            )
        except Exception:
            pass
    return out
