# Performance Optimizations — VEO Pipeline Pro

## Startup speed

| Optimization | Before | After | Savings |
|--------------|--------|-------|---------|
| Lazy tab loading | Import 8 tabs upfront | Import on first nav click | ~1-3 sec |
| `--onedir` PyInstaller | `--onefile` extracts to temp | Direct exe + DLLs | 3-5× faster |
| Splash duration | 1500ms fake delay | 600ms (real load time) | ~900ms |
| `app.processEvents()` | Splash + window race | Splash visible during build | Perceived smoother |

Total cold start estimate: **~12s → ~3s** on average Windows PC.

## Memory

- Lazy tab loading: ~80MB → ~30MB initial RSS
- Tabs released via `deleteLater` when replacing placeholder
- Settings/config loaded once, cached on instance

## Generation throughput

`workflow_run_control.get_max_in_flight()` controls parallel video gens.

Default: 1 (sequential, safest for account flag avoidance).

To raise: set `max_in_flight` in `data_general/config.json` (typical: 2-3 for paid accounts, 1 for free).

```json
{"max_in_flight": 2}
```

## Drive upload (PC post_processor)

- `MediaFileUpload(resumable=True)` — resumes on network blip
- Service-account auth cached per process

## VPS pickup

- Atomic `fcntl.flock` lock — no TOCTOU
- 3× retry with backoff on download fail
- Status `error` rows retried next cron tick

## What NOT to optimize (yet)

- ~~Multi-threaded image gen~~ — Veo3/Imagen API rate-limits per account
- ~~Cython compile~~ — Python overhead < network/IO
- ~~Native C++ Qt~~ — diminishing returns vs PyQt6

## Profiling commands

```powershell
# Startup time
Measure-Command { Start-Process VEO_Pipeline_Pro.exe -Wait }

# Memory
Get-Process VEO_Pipeline_Pro | Select-Object WS, CPU
```

```python
# Tab build time (dev mode)
import time
t0 = time.time()
# ... navigate tab ...
print(f"build {key}: {(time.time()-t0)*1000:.0f}ms")
```
