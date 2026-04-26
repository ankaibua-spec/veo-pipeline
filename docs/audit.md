# Security Audit — RUN_VEO 4.0 V2.2.6

## Original tool findings (before cleanup)

| Item | Risk | File | Status |
|------|------|------|--------|
| Author personal info: `Nguyễn Tuấn Anh`, `0879.345.345`, Zalo `zalo.me/g/ugjxpz129` | PII / tracking | `branding_config.py` | ✅ wiped |
| OpenAI JWT bearer token (`anh.nta95@gmail.com`, ChatGPT free) | Credential leak (already expired 2026-03-09) | `SORA_API_UPLOAD_IMAGE.py` line 20 | ✅ wiped |
| HMAC license secret `7c1e4b9a...` | Backend-shared secret | `License.py` | ✅ removed |
| Phone-home to Google Apps Script `AKfycbwavlawY-ksy...` | Telemetry: machine_id + license + name/phone sent to author | `License.py` | ✅ disabled |
| Anti-tamper / checksum | None found | — | ✅ N/A |
| Auto-update mechanism | None found | — | ✅ N/A |
| Backdoor / reverse shell / file exfil | None found | — | ✅ clean |

## Remaining HTTP calls (legitimate AI services)

These are intended for tool functionality:

| Endpoint | Purpose |
|----------|---------|
| `aisandbox-pa.googleapis.com` | Google Veo3 video gen API |
| `labs.google` | Google Flow login + UI |
| `accounts.google.com` | Google OAuth |
| `grok.com`, `assets.grok.com`, `imagine-public.x.ai` | Grok video gen |
| `sora.chatgpt.com` | OpenAI Sora upload |
| `localhost:9222` | Chrome DevTools (local) |

## Annoyances (not security)

- `chrome_process_manager.py` calls `os.system("pkill Chrome")` and `kill -9` on Chrome processes when tool starts. **Will close your other Chrome tabs.** Mitigation: run tool with separate Chrome profile (Brave / Chrome Beta) or patch the pkill calls to no-op.

## Cleanup actions performed

1. `branding_config.py`: replaced author info with generic placeholders
2. `SORA_API_UPLOAD_IMAGE.py`: wiped hardcoded JWT token
3. `License.py`: replaced entire phone-home logic with bypass that calls `main.main()` directly
4. All references to `script.google.com/macros/.../exec` URL replaced with `https://localhost/disabled`

## Verification commands

```bash
# Should return nothing:
grep -r "Nguyễn Tuấn Anh\|0879.345.345\|anh.nta95\|AKfycbwavla" tool/

# Should return nothing:
grep -r "eyJhbGciOiJSUzI1NiIs" tool/

# Should show only no-op bypass:
cat tool/License.py
```

## Verdict

**Safe to use** after cleanup. Tool's remaining behavior is restricted to legitimate AI service endpoints (Veo3, Grok, Sora, OAuth). No telemetry to author. No data exfiltration. No persistence beyond local config files.
