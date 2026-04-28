#!/bin/bash
# VPS auto-updater for veo-pipeline.
# Cron: 0 */6 * * * /opt/veo-pipeline/vps/updater.sh
#
# Pulls latest from GitHub, reloads cron if changed.

# Fix #8: them pipefail de bat loi trong pipe
set -e
set -o pipefail

REPO_DIR="${VEO_REPO_DIR:-/opt/veo-pipeline}"
LOG="/var/log/veo-updater.log"
TG_BOT="${VEO_TG_BOT:-}"
TG_CHAT="${VEO_TG_CHAT:-}"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Fix #8: refactor tg() de tranh command injection qua commit message
# Nhan main message ($1) va optional notes ($2) rieng biet
# Dung jq --arg de escape an toan, khong noi chuoi truc tiep vao JSON
tg() {
    [ -z "$TG_BOT" ] && return
    local main_msg="$1"
    local notes="${2:-}"
    local full_text
    if [ -n "$notes" ]; then
        full_text="${main_msg}"$'\n\n'"${notes}"
    else
        full_text="${main_msg}"
    fi
    local payload
    payload=$(jq -n \
        --arg c "$TG_CHAT" \
        --arg t "$full_text" \
        '{chat_id:$c, text:$t, parse_mode:"HTML"}') || return
    curl -s -m 5 -o /dev/null -X POST \
        "https://api.telegram.org/bot${TG_BOT}/sendMessage" \
        -H "Content-Type: application/json" \
        --data "$payload" || true
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

# Fix #8: lay CHANGES truoc khi pull, khong noi chuoi vao URL hay JSON truc tiep
# jq se xu ly escape an toan qua --arg
CHANGES=$(git log --oneline "$LOCAL..$REMOTE" | head -10)
log "pulling..."
if git pull --rebase --autostash >>"$LOG" 2>&1; then
    log "pulled"
    # Reload cron neu crontab thay doi
    if [ -f /etc/cron.d/veo-pickup ]; then
        log "reloading cron"
        systemctl reload cron 2>/dev/null || systemctl reload crond 2>/dev/null || true
    fi
    # Fix #8: truyen message va notes rieng biet, khong noi chuoi
    tg "VEO pipeline VPS updated: <code>${LOCAL:0:8}</code> to <code>${REMOTE:0:8}</code>" "$CHANGES"
else
    log "pull failed"
    tg "VEO pipeline VPS update FAILED — see /var/log/veo-updater.log"
    exit 1
fi
