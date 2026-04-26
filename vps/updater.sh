#!/bin/bash
# VPS auto-updater for veo-pipeline.
# Cron: 0 */6 * * * /opt/veo-pipeline/vps/updater.sh
#
# Pulls latest from GitHub, reloads cron if changed.

set -e
REPO_DIR="${VEO_REPO_DIR:-/opt/veo-pipeline}"
LOG="/var/log/veo-updater.log"
TG_BOT="${VEO_TG_BOT:-}"
TG_CHAT="${VEO_TG_CHAT:-}"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

tg() {
    [ -z "$TG_BOT" ] && return
    curl -s -m 5 -o /dev/null -X POST "https://api.telegram.org/bot${TG_BOT}/sendMessage" \
        -H "Content-Type: application/json" \
        --data "$(jq -n --arg c "$TG_CHAT" --arg t "$*" '{chat_id:$c,text:$t,parse_mode:"HTML"}')" || true
}

cd "$REPO_DIR" || { log "REPO_DIR=$REPO_DIR not found"; exit 1; }

LOCAL=$(git rev-parse HEAD)
git fetch origin main >/dev/null 2>&1
REMOTE=$(git rev-parse origin/main)

log "local=${LOCAL:0:8} remote=${REMOTE:0:8}"

if [ "$LOCAL" = "$REMOTE" ]; then
    log "up to date"
    exit 0
fi

CHANGES=$(git log --oneline "$LOCAL..$REMOTE" | head -10)
log "pulling..."
if git pull --rebase --autostash >>"$LOG" 2>&1; then
    log "✅ pulled"
    # Reload cron in case crontab changed
    if [ -f /etc/cron.d/veo-pickup ]; then
        log "reloading cron"
        systemctl reload cron 2>/dev/null || systemctl reload crond 2>/dev/null || true
    fi
    tg "🔄 <b>VEO pipeline VPS updated</b>%0A<code>${LOCAL:0:8}</code> → <code>${REMOTE:0:8}</code>%0A%0A<pre>${CHANGES}</pre>"
else
    log "❌ pull failed"
    tg "🔴 <b>VEO pipeline VPS update FAILED</b>%0Asee /var/log/veo-updater.log"
    exit 1
fi
