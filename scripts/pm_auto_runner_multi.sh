#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
INTERVAL=${1:-600}
STATUS_DIR="data/polymarket/runtime"
LOG_FILE="$STATUS_DIR/pm_auto_runner_multi.log"
mkdir -p "$STATUS_DIR"
STRATS=(
  "strategies/br_tail_v1.json"
  "strategies/test1_br_copy.json"
  "strategies/test2_follow_br.json"
  "strategies/test3_combined.json"
)

log(){
  echo "[$(date -u +%FT%TZ)] $*" >> "$LOG_FILE"
}

trap 'log "ERROR"; exit 1' ERR
trap 'log "STOP"' EXIT

run_once() {
  local strat="$1"
  local base
  base=$(basename "$strat" .json)
  local tag="${base}_$(date -u +%H%M%S)"
  local out
  local orders results
  local reasons
  log "RUN strategy=${base}"
  out=$(python3 scripts/pm_paper_loop.py --strategy "$strat" --tag "$tag" --scan-pages 120 --cache-age-sec 120 || true)
  echo "$out" > "$STATUS_DIR/${base}_status.json"
  orders=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("orders_generated",0)) if t else 0)' 2>/dev/null || echo 0)
  results=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("results_backfilled",0)) if t else 0)' 2>/dev/null || echo 0)
  reasons=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip();
import collections
if not t:
  print("");
  raise SystemExit
j=json.loads(t)
sel=j.get("selection_reasons",{}) or {}
items=sorted(sel.items(), key=lambda kv:-kv[1])[:3]
print(" ".join([f"{k}:{v}" for k,v in items]))
' 2>/dev/null || echo "")
  log "OK strategy=${base} orders=${orders} results=${results} reasons=${reasons}"
}

log "START interval=${INTERVAL}"

while true; do
  # guard check
  scripts/system_protection_guard.sh >/dev/null 2>&1 || true
  if [[ -f data/system_guard/guard.flag ]]; then
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"status\":\"paused_guard\"}" > "$STATUS_DIR/auto_loop_status.json"
    log "PAUSED guard"
    sleep "$INTERVAL"
    continue
  fi

  for strat in "${STRATS[@]}"; do
    run_once "$strat"
    sleep 2
  done

  sleep "$INTERVAL"
done
