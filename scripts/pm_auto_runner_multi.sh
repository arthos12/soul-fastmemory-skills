#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
INTERVAL=${1:-600}
STATUS_DIR="data/polymarket/runtime"
mkdir -p "$STATUS_DIR"
STRATS=(
  "strategies/br_tail_v1.json"
  "strategies/test1_br_copy.json"
  "strategies/test2_follow_br.json"
  "strategies/test3_combined.json"
)

run_once() {
  local strat="$1"
  local base
  base=$(basename "$strat" .json)
  local tag="${base}_$(date -u +%H%M%S)"
  local out
  out=$(python3 scripts/pm_paper_loop.py --strategy "$strat" --tag "$tag" --scan-pages 120 --cache-age-sec 120 || true)
  echo "$out" > "$STATUS_DIR/${base}_status.json"
}

while true; do
  # guard check
  scripts/system_protection_guard.sh >/dev/null 2>&1 || true
  if [[ -f data/system_guard/guard.flag ]]; then
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"status\":\"paused_guard\"}" > "$STATUS_DIR/auto_loop_status.json"
    sleep "$INTERVAL"
    continue
  fi

  for strat in "${STRATS[@]}"; do
    run_once "$strat"
    sleep 2
  done

  sleep "$INTERVAL"
done
