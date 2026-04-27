---
name: PC Migration Plan — VEO Pipeline Pro full PC operation
description: Plan to migrate every remaining VPS-side pipeline stage to PC Windows now that Veo3 gen on PC works 100% via residential IP
type: project-plan
status: DRAFT (awaits user decision points before phase 1)
authors: AI Company OS — Engineering + QA + Ops
date: 2026-04-27
---

## Context

Veo3 gen on PC (RUN_VEO 4.0 cleaned + residential Chrome) is the only stage that ever needed PC. All downstream stages still live on VPS. This plan moves the rest so the PC owns the pipeline end-to-end and the VPS becomes optional (notify + dashboard only).

Affected pipelines on VPS today: **English Pronunciation Factory** (`/opt/english-pronunciation/`, port 3001 — actually folded into english-shorts-factory), **English Shorts Factory** (karaoke 20/day), **English Story Pipeline** (drama 4/day), **ASMR Factory** (3/day, in restoration), **Fashion TikTok** (Flow2API affiliate, currently broken).

## 1. Stage inventory (current VPS load)

| # | Stage | Where | Files / cron | Inputs | Outputs |
|---|-------|-------|-------|--------|---------|
| 1 | Drive pickup poll | VPS cron `*/5` | `/root/veo-pipeline/vps/veo_drive_pickup.py` → `/etc/cron.d/veo-pickup` | Drive folder ID, service-account JSON | Insert `veo_drive_files` row in `/opt/english-pronunciation/storage/database.db` |
| 2 | Content schedule generator | VPS node-cron `0 0 * * *` | `worker.js` `_ensureSchedule()` + `contentStrategy.js` | DB `content_schedule`, theme rotation | 30-day schedule rows |
| 3 | Production cron (15-min poll) | VPS node-cron `*/15` | `worker.js` `_runScheduledTasks()` | `content_schedule` rows due | Calls `pipeline.process()` |
| 4 | Script generation | VPS | `scriptGenerator.js` (Groq → fallback) | Topic + niche from schedule | `{title, description, overlay_top, overlay_bottom, image_prompts}` |
| 5 | TTS Edge | VPS | `ttsService.js` | Script text | `audio.mp3` + WordBoundary JSON |
| 6 | Background image gen | VPS | `imageGenService.js` (Kie.ai nano-banana 9:16) | image_prompt | PNG 1080×1920 |
| 7 | Karaoke render | VPS FFmpeg | `videoRenderer.js` (~498 lines) | bg PNG + mp3 + WordBoundary + overlay text | final 1080×1920 mp4 |
| 8 | Drive backup | VPS | `driveService.js` | mp4 path | Drive file id |
| 9 | YouTube upload (CH1/CH2) | VPS | `youtubeService.js`, `youtubeService2.js`, `seoPostUpload.js` | mp4 + metadata | YouTube videoId, URL |
| 10 | English Story batch render | VPS cron `0 18 * * *` | `/root/english-story-pipeline/scripts/batch_render.sh` | Combo dict | 4 long-form mp4 + thumbs |
| 11 | English Story SEO/analytics | VPS cron weekly+daily | `seo_keyword_research.py`, `seo_analytics_report.js`, `seo_optimizer.py` | YouTube Analytics API | DB updates |
| 12 | Fashion TikTok loop | VPS service `fashion-tiktok.service` | `affiliatePipeline.js` + `loop.sh` | Flow2API + Drive | mp4 + TikTok post |
| 13 | OAuth tokens | VPS SQLite `youtube_tokens` (id=1 CH1, id=2 CH2) | `database.db` | Google Sign-in | Refresh token used by uploader |
| 14 | Dashboard / Flask + Express UI | VPS port 3001 + 3002 + nginx | `server.js`, `english-shorts-factory.service`, `asmr-factory.service` | DB | Web UI on `app.trbm.shop` |
| 15 | Telegram notify | VPS | `telegramService.js` | Events | Channel `-1003678583405`, `-1003375527350`, etc |

## 2. Migration assessment per stage

| Stage | Move to PC? | Trade-off / blocker | Effort |
|-------|-------------|---------------------|--------|
| 1 Drive pickup | **DELETE** — useless once render is on PC (the file is already there) | None | 1 h |
| 2 Schedule gen | **PC** — pure JS over SQLite, no network | DB must live on PC; back up to Drive | 2 h |
| 3 Production cron | **PC** — replace `cron` with Windows Task Scheduler or keep `node-cron` inside `post_processor.py` companion | PC must be powered + logged-in 24/7 | 4 h |
| 4 Script gen (Groq) | **PC** — pure HTTPS to Groq | Move `GROQ_API_KEY` to PC `.env` | 1 h |
| 5 Edge TTS | **PC** — `edge-tts` runs on Windows fine | None | 1 h |
| 6 Kie.ai image | **PC** — pure HTTPS | Key on PC | 1 h |
| 7 FFmpeg karaoke | **PC** — already a winning move (PC GPU faster than VPS) | Install ffmpeg + fonts on Windows | 4 h |
| 8 Drive backup | **PC** — already done in `pc/post_processor.py` | None | 0 |
| 9 YouTube upload | **PC** — `googleapis` works the same | Move OAuth tokens; redirect URI must match (`http://localhost`) | 4 h |
| 10 Story batch | **PC** — `run.py` is plain Python+FFmpeg+Edge TTS | Long render (60-80 min) — PC must stay awake at 18:00 UTC | 6 h |
| 11 SEO analytics | **stay on VPS** OR move — runs once/day, doesn't need PC | Cheap to leave on VPS | 0 if stay |
| 12 Fashion TikTok | **PC** if revived (Flow2API browser is the same trick) | VMOS ADB step still needs network — works from PC | 8 h (currently broken) |
| 13 OAuth tokens | **PC SQLite** — copy `youtube_tokens` rows + new redirect URI on Google Console | One-time re-auth flow if redirect changes | 2 h |
| 14 Dashboard | **stay on VPS** — public URL `app.trbm.shop` cannot point at home IP | Hybrid: dashboard reads via Drive-shared DB or cloud KV | 0 if read-only |
| 15 Telegram | **PC** native, no change | None | 0 |

**Verdict:** Stages 1–10, 12–13, 15 are PC-friendly. Stages 11, 14 are best left on VPS for cost + public reachability.

## 3. Recommended split (final architecture)

```
PC Windows (always-on, residential IP)
├── tool/             RUN_VEO 4.0 GUI                  [Veo3 gen — already works]
├── pc/scheduler/     node + node-cron (replaces VPS worker.js)
│   ├── schedule.js   30-day schedule generator
│   ├── produce.js    script + TTS + image + ffmpeg karaoke
│   ├── upload.js     YouTube CH1+CH2 (googleapis)
│   └── notify.js     Telegram + Zalo
├── pc/story/         English Story renderer (Python venv)
├── pc/post_processor (existing) — Drive sync any leftover
├── data/factory.db   primary SQLite (canonical)
└── data/oauth/       google_creds, youtube_tokens.json
              ↓ mirror via Drive every 15 min
VPS Linux (cheap, public IP)
├── dashboard         read-only mirror of factory.db (rclone or rsync)
├── nginx + SSL       app.trbm.shop / english.trbm.shop / asmr.trbm.shop
├── seo cron          analytics report + optimizer (lightweight)
└── outage relay      if PC offline >2h → Telegram alert + show last-known status
```

Justification: PC owns generation + upload (where Google blocks datacenter IPs). VPS keeps the public URL, the SSL, and the reporting cron — none of those touch Google Flow / Veo / YouTube upload limits.

## 4. Phased plan

### Phase 1 — Bootstrap PC scheduler (Week 1, ~2 days work)
**Deliverable:** PC produces + uploads 1 English Short end-to-end, no VPS involvement.
**Files to create:**
- `C:\veo_pipeline\pc\scheduler\package.json` (node-cron, googleapis, better-sqlite3, axios)
- `pc\scheduler\schedule.js` — port `contentStrategy.js`
- `pc\scheduler\produce.js` — port `pipeline.js` + `scriptGenerator.js` + `videoRenderer.js`
- `pc\scheduler\upload.js` — port `youtubeService.js` + `youtubeService2.js`
- `pc\scheduler\db.js` — better-sqlite3 wrapper to `data\factory.db`
- `data\factory.db` — copy of `/opt/english-shorts-factory/storage/database.db`
- `pc\scheduler\.env` — GROQ, KIE_AI, YOUTUBE_OAUTH (CH1+CH2)
**Modify:** Google Cloud OAuth client → add `http://localhost:53682/oauth/callback` redirect URI.
**Time:** 16 h.

### Phase 2 — Cutover English Shorts (Week 2, 1 day)
**Deliverable:** 20 video/day produced by PC, VPS worker stopped.
**Steps:** disable `english-shorts-factory.service` cron schedules (keep web UI alive), point YouTube uploads to PC service, run 48-hour parallel test (PC + VPS both schedule but only PC uploads).
**Files modify:** `/opt/english-shorts-factory/backend/services/worker.js` — gate `_runScheduledTasks` behind `process.env.WORKER_ROLE === 'producer'` (default: dashboard-only).
**Rollback:** flip env var, VPS resumes.
**Time:** 8 h.

### Phase 3 — Add Story + ASMR (Week 3, 2 days)
**Deliverable:** All 3 long-form pipelines on PC.
**Files create:** `pc\story\` (clone `/root/english-story-pipeline/`), `pc\asmr\` (port from `/opt/asmr-factory/`).
**Cron move:** delete `/etc/cron.d/english-story`, replace with Windows Task Scheduler tasks at same UTC times.
**SEO scripts:** keep on VPS (read DB mirror).
**Time:** 16 h.

### Phase 4 — Fashion TikTok revival (Week 4, optional, 1-2 days)
Currently broken (Flow2API depleted). If user wants it back, the same residential-IP trick works in `RUN_VEO` already → port `affiliatePipeline.js` to PC and call VMOS ADB over Tailscale or LAN.
**Time:** 12 h.

### Phase 5 — DB mirror + outage relay (Week 4-5, 1 day)
**Deliverable:** VPS dashboard always shows live data; if PC down >2h Telegram alert.
**Files create:** `pc\scheduler\sync_db.js` — every 15 min, upload `factory.db` to Drive folder; VPS `vps/db_mirror.sh` cron `*/15` pulls it. `vps/outage_check.sh` cron `*/30` — if last upload >2h → Telegram.
**Time:** 8 h.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **PC offline / power cut** | Whole pipeline stops | UPS + auto-login + Task Scheduler "run whether logged in or not" + outage relay (Phase 5) |
| **Windows update reboot** | Tasks miss schedule | Disable auto-reboot on active hours; schedule restart Sun 04:00 |
| **OAuth redirect break** | Upload fails after re-auth | Phase 1 sets new `localhost` redirect; keep VPS redirect as warm spare for 30 days |
| **YouTube quota** | 10k units/day = 2.8k used by 20 Shorts; story uploads add 140 each | Same as today — no change. Quota is per-channel not per-host |
| **Drive desktop sync conflicts** | Two writers (PC + VPS) on same DB | Make PC the single writer; VPS only reads mirror |
| **node-cron drift on Windows sleep** | Misses 15-min cron when laptop sleeps | Disable sleep + Task Scheduler "wake to run task" |
| **Groq / Kie.ai key leak on PC** | Bill shock | `.env` 600 perms, no commit, rotate quarterly |
| **Public IP reveal via Telegram bot** | Privacy | All outbound via PC NAT — fine, no inbound port open |

## 6. AI Company workflow

Tasks runnable in parallel at the same calendar week:

**Phase 1 (parallel):**
- **Engineering A** — port scheduler (`schedule.js` + `produce.js`)
- **Engineering B** — port uploader + OAuth migration
- **Product** — query NotebookLM "best practice for Windows Task Scheduler vs node-cron 24/7", "googleapis OAuth refresh on offline desktop"
- **QA** — write end-to-end test plan: 1 video produced + uploaded + visible on YouTube + tracked in DB

**Phase 2 (sequential after 1):**
- **Ops** — staged rollout, env-var gate, 48-h dual-run, Telegram heartbeat
- **QA** — line-by-line review of `worker.js` gate flag + `factory.db` schema diff

**Phase 3 (parallel):**
- **Eng A** — Story pipeline port
- **Eng B** — ASMR pipeline port
- **QA** — render-quality regression (compare 5 PC outputs vs 5 VPS outputs frame-by-frame)

**Ops final:** commit + push each phase to `ankaibua-spec/veo-pipeline`, update `docs/setup.md`, Zalo notify.

## 7. Decision points for user (please confirm before phase 1)

1. **PC always-on?** Anh có thể giữ PC chạy 24/7 (UPS + không sleep) hay PC tắt ban đêm? → quyết định cron nào chạy được.
2. **Backup VPS for outages?** Khi PC offline >2 h, có muốn VPS *tạm* tự render lại (slower but unblocked) hay chỉ alert + skip slot?
3. **OAuth re-consent?** Đồng ý thêm `http://localhost:53682/oauth/callback` vào Google Cloud Console + re-login 2 channel CH1/CH2? (one-time, ~5 min)
4. **DB single writer?** Confirm PC là canonical writer, VPS chỉ mirror read-only? (an toàn hơn 2-way sync)
5. **Fashion TikTok revival** — phase 4 có làm hay drop? (currently broken, proxies/credit hết)
6. **Domain split** — `english.trbm.shop` + `app.trbm.shop` vẫn trỏ VPS (cho dashboard), đúng không?
7. **Tailscale / LAN access PC↔VPS?** Để VPS query factory.db hoặc trigger PC khi cần — cần mở 1 đường an toàn (Tailscale free tier OK).
8. **Migration window** — chấp nhận 48h dual-run (PC + VPS cùng chạy, chỉ PC upload) hay cutover hard?

> Trả lời 8 câu trên → AI Company OS sẽ kick off Phase 1 ngay (Engineering A+B + Product NLM song song trong 1 session, QA review sau commit).
