#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/root/.openclaw/workspace"
LOG="$WORKDIR/data/system_guard/guard_watch_10m.log"

mkdir -p "$WORKDIR/data/system_guard"

log(){
  echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"
}

start_fast_scan(){
  if pgrep -f "pm_fast_scan_trade.py" >/dev/null 2>&1; then
    return 0
  fi
  log "start pm_fast_scan_trade"
  PM_LOOP_INTERVAL=3 nohup python3 "$WORKDIR/scripts/pm_fast_scan_trade.py" >/tmp/pm_fast_scan_trade.log 2>&1 &
}

while true; do
  # refresh guard status
  bash "$WORKDIR/scripts/system_protection_guard.sh" >/dev/null 2>&1 || true

  if [[ -f "$WORKDIR/data/system_guard/guard.flag" ]]; then
    log "guard.flag active -> skip restart"
  else
    start_fast_scan
    log "ok running"
  fi

  sleep 600
 done
