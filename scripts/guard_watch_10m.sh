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

check_fast_scan(){
  if pgrep -f "python3 .*pm_fast_scan_trade.py" >/dev/null 2>&1; then
    # also require fresh log update (avoid zombie process)
    local log_file="$WORKDIR/data/polymarket/runtime/pm_scan_trade_loop.log"
    if [[ -f "$log_file" ]]; then
      local now=$(date +%s)
      local mtime=$(stat -c %Y "$log_file" 2>/dev/null || echo 0)
      local age=$((now-mtime))
      if (( age > 300 )); then
        log "fast_scan stale (${age}s) -> restart"
        start_fast_scan
        return 0
      fi
    fi
    log "fast_scan ok"
  else
    log "fast_scan missing -> restart"
    start_fast_scan
  fi
}

while true; do
  # refresh guard status
  bash "$WORKDIR/scripts/system_protection_guard.sh" >/dev/null 2>&1 || true

  if [[ -f "$WORKDIR/data/system_guard/guard.flag" ]]; then
    log "guard.flag active -> skip restart"
  else
    check_fast_scan
    log "ok running"
  fi

  sleep 600
 done
