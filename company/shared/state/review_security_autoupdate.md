# Security Audit — VEO Pipeline Pro Auto-Update Flow

Hacker POV. Scope: auto_update.py, launcher_pro.py, drive_settings.py, license_dialog.py.

## CRITICAL

- **[CRITICAL] auto_update.py:79 — No hash/signature verification on downloaded ZIP (RCE)**
  - URL is read from GitHub API JSON (`browser_download_url`), then streamed to disk and executed via `apply_update`. No `sha256`, no GPG/cosign signature, no pinned cert. GitHub repo `ankaibua-spec/veo-pipeline` is **public and writable by anyone with org/repo write access** — leaked PAT, compromised maintainer, or attacker-uploaded "asset" with same name → arbitrary EXE replacement on every installed client.
  - PoC: attacker pushes a release with malicious `VEO_Pipeline_Pro_Windows.zip` containing trojan `VEO_Pipeline_Pro.exe` → every client auto-downloads on next launch (`QTimer.singleShot(1500, ...)`) → robocopy `/MIR` overwrites real binary → trojan launches with full user privileges + access to Drive credentials, license file, Telegram tokens.
  - Fix: embed publisher pubkey in code. Sign the ZIP with `minisign`/`cosign`/Authenticode-detached signature in CI, ship `.zip.sig` as second asset, verify before extract. Minimum bar: pin `sha256` in a signed `manifest.json` asset and only trust that. Refuse to apply if signature fails.

- **[CRITICAL] auto_update.py:138-177 — Command injection via tempdir / username in robocopy .bat (Windows)**
  - `target_dir`, `extract_dir`, `backup_dir`, `exe_path`, `pid` are all `f`-string interpolated into a `.bat` file with **no quoting validation**. `target_dir` derives from `Path(sys.executable).parent` — if user installs to `C:\Users\Bob & whoami > C:\pwn.txt\VEO\` or any path with `&`, `|`, `^`, `%`, `"`, the cmd.exe parser breaks out of the quoted argument. Windows allows `&` `^` `%` in usernames/folder names. `tempfile.gettempdir()` returns `%TEMP%` which contains the username (`C:\Users\<name>\AppData\Local\Temp`).
  - PoC: install to `C:\Users\evil & calc & echo \VEO\`. The line `if exist "C:\Users\evil & calc & echo \VEO\_backup" rmdir...` parses as `if exist "C:\Users\evil "` then `& calc &` runs calc. Same for `extract_dir` if `%TEMP%` is attacker-controlled (e.g. via `TMP`/`TEMP` env vars set by another local process before launch).
  - Also `del "%~f0"` self-delete — fine, but the rest of script trusts non-validated interpolation.
  - Fix: validate paths against a whitelist regex `^[A-Za-z0-9 _\-.\\:]+$` before writing the .bat, **reject** if any of `& | ^ % " < > '` present. Better: rewrite the swap logic in pure Python using a tiny helper EXE shipped in the bundle, or use PowerShell with `-File` + `-Command` and pass args through `argv` (no shell parsing).

- **[CRITICAL] drive_settings.py:208-248 — OAuth refresh_token import has no auth, no integrity check, no origin pinning**
  - `urllib.request.urlopen("https://app.trbm.shop/api/drive/credentials")` returns `{client_id, client_secret, refresh_token}` and writes it to `~/.veo_pipeline/drive_credentials.json` with no API key, no per-user token, no HMAC. **Anyone who hits that endpoint gets the Drive refresh_token of the VPS owner** → full Drive read/write of `truonghoa.gtvt@gmail.com`. Even the URL itself is a single fixed `APP_TRBM_BASE` — no DNS pinning, no cert pinning, system trust store only. If `app.trbm.shop` DNS gets hijacked / domain expires / cert mis-issued, every installed client fetches attacker-controlled credentials and silently swaps them in.
  - PoC: `curl https://app.trbm.shop/api/drive/credentials` from anywhere on the internet → if endpoint exists, returns refresh_token in cleartext JSON. Or stand up evil DNS for `app.trbm.shop` on a victim LAN → MITM the TLS with a rogue cert (cert pinning would block this).
  - Fix: require `Authorization: Bearer <license_key>` header, validate license server-side, scope token to that license. Pin the TLS leaf cert SPKI hash in the client. Audit / rate-limit the endpoint. Return short-lived access tokens, never raw refresh_tokens.

## HIGH

- **[HIGH] auto_update.py:96-103 — `_safe_extract` zip-slip check is bypassable on Windows (case + symlink + reserved names)**
  - `str(target).startswith(str(dest_resolved))` — string prefix on resolved paths. `Path.resolve()` does **not** resolve through zip-internal symlinks (zips can carry symlink entries on POSIX-extracted machines but Windows ignores). On Windows the bigger holes:
    1. Drive letter case: `dest_resolved="C:\Users\..."` vs `target="c:\users\..."` (extractall preserves case from member name). `startswith` is case-sensitive on Python's str — a member like `..\..` after `resolve()` still works because it canonicalises, but a sibling-prefix attack works: `dest=C:\Temp\veo_update_extract`, attacker member resolves to `C:\Temp\veo_update_extract_evil\x.exe` → `startswith("C:\Temp\veo_update_extract")` is **True** (no separator check) → escapes containment.
    2. `extractall` then runs anyway — even if `_safe_extract` raised on member N, members 0..N-1 already extracted (no atomic). Partial writes become attack surface.
  - PoC: zip with a single member `../veo_update_extract_pwn/payload.dll` — resolves to sibling folder, passes prefix check, drops file outside intended dir. Or member named `aux.exe` / `con` (reserved Windows names) crashes `Path.resolve` differently per Python version.
  - Fix: use `os.path.commonpath([dest_resolved, target]) == dest_resolved` (proper boundary check), reject any member with absolute path / drive letter / `..` BEFORE any extraction, extract member-by-member with `zf.open()` + manual write — never `zf.extractall()`.

- **[HIGH] auto_update.py:132-184 — TOCTOU race between extract and robocopy**
  - Flow: extract to `%TEMP%/veo_update_extract` → write .bat → spawn cmd.exe → exit Python. The .bat then runs robocopy `/MIR` from that dir into `target_dir`. **Window of seconds-to-minutes** where any local user / malware can `rmdir + mklink` or replace files in `%TEMP%/veo_update_extract` because `%TEMP%` is per-user-writable but the extracted ZIP contents have NO integrity check after extraction.
  - PoC: malware watches `%TEMP%\veo_update_extract\` with `ReadDirectoryChangesW`, when populated swaps `VEO_Pipeline_Pro.exe` for trojan, robocopy mirrors trojan into install dir. Even more reliable: malware drops files at predictable extract path BEFORE update fires, then `_safe_extract` → `extractall` doesn't clear, robocopy /MIR copies attacker's pre-planted file.
  - Mitigation: line 122 `shutil.rmtree(extract_dir, ignore_errors=True)` runs but `ignore_errors=True` swallows failures (e.g. attacker-held file lock leaves stale content).
  - Fix: extract to a **freshly-created random** dir (`tempfile.mkdtemp(prefix="veo_upd_")`), set restrictive ACL (`icacls /inheritance:r /grant:r "%USERNAME%:F"`), verify hash of every extracted file against signed manifest BEFORE robocopy, never reuse a fixed path under `%TEMP%`.

- **[HIGH] auto_update.py:146 — PID race in tasklist wait loop**
  - `tasklist /FI "PID eq {pid}"` — Windows reuses PIDs aggressively. App exits, PID 12345 freed, OS reassigns to `svchost.exe`, the wait loop sees it as "alive", spins for full 60s then `:proceed` and slams robocopy /MIR on top of a running app. Also reverse: PID exits in <1s (counter still 0), loop never enters, robocopy runs while app may still hold file locks → robocopy gets `errorlevel 8` → triggers rollback even though new files weren't applied → app is fine but UX shows "failed".
  - PoC: rapid app crash + immediate Windows service spawn reusing PID. Not exploitable for code exec but kills update reliability and the rollback codepath itself can corrupt install if backup mirror was incomplete.
  - Fix: pass a one-time secret + image-name match: `tasklist /FI "PID eq {pid}" /FI "IMAGENAME eq VEO_Pipeline_Pro.exe"`. Or have Python write its PID + start-time to a file, .bat checks both via `wmic process where ProcessId=... get CreationDate`.

- **[HIGH] auto_update.py:157,160,163 — robocopy /MIR + rollback corruption window (data loss)**
  - `/MIR` deletes everything in destination not in source. Sequence:
    1. Mirror `target_dir` → `backup_dir` (line 157). If disk full / partial, exit code is silently `>NUL`'d — script keeps going.
    2. Mirror `extract_dir` → `target_dir`. Same — errors hidden.
    3. If errorlevel 8: mirror `backup_dir` → `target_dir`. **If backup was partial in step 1**, rollback nukes legitimate files that weren't backed up.
  - User loses: license.json (under `~`, safe), but also any user-modified files inside install dir (custom config, plugins, user-edited prompts). Onedir PyInstaller bundles often have user-mutable resource files — all gone with /MIR.
  - PoC: fill disk to 99%, trigger update during low free space → backup partial → main copy fails (errorlevel 8) → rollback from incomplete backup → install dir nuked.
  - Fix: capture robocopy errorlevel of step 1, abort + alert if `>= 8` BEFORE step 2 runs. Also use `/COPY:DAT` not full `/MIR` so ACLs don't get clobbered. Add `/L` dry-run pre-check.

- **[HIGH] license_dialog.py:35-42 — Machine ID trivially spoofable + truncated hash**
  - Fallback path uses `uuid.getnode()` (MAC, easily spoofed via `Set-NetAdapterAdvancedProperty -DisplayName "Network Address"` no admin needed) + `platform.node()` (hostname, env-overridable on Linux via `HOSTNAME`, set-able on Windows). Even Windows path: `winreg.OpenKey(HKLM\SOFTWARE\Microsoft\Cryptography, MachineGuid)` is **HKLM** so admin-only to write, but: a) attacker on victim's box already gets license-bypass via `VEO_BYPASS_LICENSE=1` env var set in their own session (line 66), b) the SHA256 is **truncated to 24 hex chars (96 bits)** → birthday collision feasible at scale (~2^48 = 280T machines for 50% collision), and pirates can grind for collisions that match an issued license.
  - Also: license file at `~/.veo_pipeline/license.json` is plaintext JSON. No HMAC, no server callback. Pirate copies the file + the (spoofable) MachineGuid → activated forever. License is a vibes-check, not a license.
  - Fix: server-side activation w/ online check (POST license_key + machine_id, server returns signed JWT bound to machine_id, expires in N days, refresh online). Use full SHA256, not truncated. Remove `VEO_BYPASS_LICENSE` env in release builds, or require it to be a signed token. Sign license.json with publisher key, verify on every launch.

- **[HIGH] license_dialog.py:158-167 — License "validation" is just a length check**
  - `if len(key_clean) < 12: warn ; else: save_license(key, machine_id())`. ANY 12-char string activates: `AAAAAAAAAAAA`, `123456789012`, copy-paste anything. The dialog literally tells the user "Tạm thời nhập: AAAA-BBBB-CCCC-DDDD" — an explicit 100% bypass shipped in production code.
  - PoC: enter `aaaa-bbbb-cccc-dddd` → activated. No revenue protection at all.
  - Fix: actual signed license check — verify `Ed25519(license_key, machine_id, expiry).verify(pubkey)` server-side or with embedded pubkey. Until that lands, do not advertise as commercial.

## MEDIUM

- **[MEDIUM] auto_update.py:23,53 — Plain HTTPS to GitHub API, no cert pinning**
  - `urllib.request` uses system CA bundle. Corporate MITM proxies / rogue CAs / future GitHub cert mis-issuance → attacker swaps `tag_name` and `browser_download_url` to point to attacker's own ZIP. Combined with the no-signature CRITICAL above, this is a one-step RCE channel.
  - Fix: pin `api.github.com` SPKI hash, or sign the release manifest separately and ignore HTTP layer.

- **[MEDIUM] drive_settings.py:215 — `urlopen(timeout=10)` no cert pinning, accepts any 200 JSON shape**
  - `data.get("oauth")` writes whatever shape arrives to disk as JSON. Malicious server (or MITM) can pollute `~/.veo_pipeline/drive_credentials.json` with a payload that, when later parsed by the Drive SDK, exploits a deserialization quirk. Lower severity than CRITICAL (still requires breaking TLS), but the lack of schema validation on parsed JSON is sloppy.
  - Fix: validate `data["oauth"]["refresh_token"]` is `str`, reject extra keys, enforce max length. Pin TLS.

- **[MEDIUM] auto_update.py:60,92,218 — `except Exception: print(...)` swallows all errors silently**
  - Auto-update failures (download corruption, partial extract, TLS error) get a `print` to stdout that nobody sees in a frozen GUI app. User believes the update worked. Combined with `subprocess.Popen` detached → the .bat may fail to even start and Python `_os._exit(0)` (line 215) still kills the live app. Result: app gone, no update applied, no error shown.
  - Fix: catch specific exceptions (URLError, BadZipFile, OSError), surface to user via QMessageBox before exit, add a sentinel file the .bat creates after success and the next launch checks.

- **[MEDIUM] launcher_pro.py:215 — `os._exit(0)` skips Qt cleanup, may leave file locks**
  - Hard exit 200ms after triggering swap means open handles to log files / SQLite DBs / Drive temp uploads aren't flushed. robocopy may then fail with "file in use" → triggers rollback path → corrupts install (per [HIGH] above). Also any background `drive_sync.start_background()` thread (line 163) holds file handles on output dir which may not be in install dir but could still race.
  - Fix: `app.quit()` + `app.processEvents()` + `sys.exit(0)`. Use a real handover: app writes PID file, .bat polls for PID file removal not for tasklist.

- **[MEDIUM] drive_settings.py:243 — Drive credentials written without restrictive perms**
  - `CRED_FILE.write_text(json.dumps(cred_data, indent=2))` → file mode is process umask (0644 typical). Other local users on shared Windows boxes (kids account, IT admin) can read OAuth refresh_token. On Windows the default ACL inherits from `~\.veo_pipeline\` which is user-only, so practical risk is lower, but on Linux/WSL this is plain-readable.
  - Fix: `os.chmod(CRED_FILE, 0o600)` after write, on Windows use `icacls` to strip Everyone/Users.

- **[MEDIUM] license_dialog.py:54-60, drive_settings.py:33-37 — "Atomic write" is not atomic on Windows**
  - `tmp.replace(target)` is `MoveFileEx(MOVEFILE_REPLACE_EXISTING)`. Atomic for the rename itself, but if another process is reading `target` mid-write you get sharing-violation. Worse: `tmp.write_text(json.dumps(...))` doesn't `fsync` — power loss between write and replace = empty `.tmp` then rename → zero-byte license/config. Next launch: `json.loads("")` → exception → license treated as missing → user re-prompted.
  - Fix: `tmp.write_text(...)` then `os.fsync(tmp.fileno())` before rename. Catch `JSONDecodeError` in `load_license` and back-up the corrupt file before regenerating.

## LOW

- **[LOW] auto_update.py:181 — `subprocess.Popen(["cmd.exe", "/c", str(bat)], close_fds=True)` — `close_fds=True` on Windows requires no `stdin/stdout/stderr` redirection (true here, OK), but `cmd.exe` resolves via PATH, not absolute path. PATH-hijack on Windows possible if attacker drops `cmd.exe` in install dir before launcher runs.
  - Fix: hardcode `C:\Windows\System32\cmd.exe` resolved via `shutil.which` at install time, or call `bat` directly via `os.startfile` since .bat is registered.

- **[LOW] launcher_pro.py:80-87 — Onboarding copies user-supplied `cred_src` to home with no validation**
  - `_sh.copy2(cred_src, dest)` — if user is tricked into picking a 5GB file as "drive_cred", we silently copy it. Not a security issue per se, more DoS / disk-fill. Also no JSON validation before copying.
  - Fix: parse JSON first, verify it has `client_email` (service account) or `refresh_token` (oauth), reject if not.

- **[LOW] license_dialog.py:151 — `t.SUPPORT_URL` opened via `webbrowser.open` — fine, but `t.AUTHOR_ZALO` rendered as HTML link concat — if `theme.py` ever takes user input that string becomes a vector. Static today, theoretical.

- **[LOW] drive_settings.py:138-145 — Telegram bot token stored plaintext in `onboarded.json`**
  - User-facing field, by design, but file has no perms hardening (see `[MEDIUM]` on perms). On Linux/WSL multi-user: token leaks to other users → they own the bot.
  - Fix: same as Drive creds — chmod 0600 after write.

- **[LOW] auto_update.py:166 — `del "%~f0"` self-delete races with the still-running cmd.exe shell**
  - Windows allows deleting a running .bat in modern versions because cmd.exe loads it line-by-line with sharing. But edge case: AV (Defender, Kaspersky) holds an exclusive scan lock on a freshly-written .bat → del fails silently → stale .bat in `%TEMP%` (info-leak: includes target_dir, PID, install layout). Cleanup never happens.
  - Fix: have the .bat write its own PID, schedule a delayed delete via `schtasks /create /tn vupd /sc once /st .... /tr "del ..." /f` or live with the leftover file (cosmetic).

## Summary

- **3 CRITICAL** (unsigned ZIP RCE, .bat injection via path, OAuth endpoint with no auth) — block release. Each is a one-step full-host compromise.
- **6 HIGH** — fix before any commercial sale (license bypass, /MIR data loss, zip-slip prefix bypass, TOCTOU on extract, PID race, machine-ID spoof).
- **6 MEDIUM** — TLS pinning, error swallowing, perms hardening, atomic-write fsync.
- **5 LOW** — defense-in-depth.

Top-3 fix order: (1) sign + verify ZIP, (2) parameterise .bat (no f-string into cmd grammar), (3) auth the `/api/drive/credentials` endpoint with license token + TLS pin.
