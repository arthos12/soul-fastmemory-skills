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

start_auto_multi(){
  if pgrep -f "pm_auto_runner_multi.sh" >/dev/null 2>&1; then
    return 0
  fi
  log "start pm_auto_runner_multi"
  nohup bash "$WORKDIR/scripts/pm_auto_runner_multi.sh" >/tmp/pm_auto_runner_multi.log 2>&1 &
}

start_auto(){
  if pgrep -f "pm_auto_runner.sh" >/dev/null 2>&1; then
    return 0
  fi
  log "start pm_auto_runner"
  nohup bash "$WORKDIR/scripts/pm_auto_runner.sh" >/tmp/pm_auto_runner.log 2>&1 &
}

while true; do
  # refresh guard status
  bash "$WORKDIR/scripts/system_protection_guard.sh" >/dev/null 2>&1 || true

  if [[ -f "$WORKDIR/data/system_guard/guard.flag" ]]; then
    log "guard.flag active -> skip restart"
  else
    start_fast_scan
    start_auto_multi
    start_auto
    log "ok running"
  fi

  sleep 600
 done
