#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
STRAT="${1:-strategies/br_v2_relaxed.json}"
TAG_PREFIX="${2:-cont}"
INTERVAL="${3:-600}"
STATUS="data/polymarket/runtime/br_loop_status.json"
mkdir -p data/polymarket/runtime
fail_count=0
while true; do
  ts=$(date -u +%FT%TZ)
  tag="${TAG_PREFIX}_$(date -u +%H%M%S)"
  out=$(python3 scripts/pm_paper_loop.py --strategy "$STRAT" --tag "$tag" --scan-pages 25 --cache-age-sec 120 || true)
  orders=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("orders_generated",0)) if t else 0)' 2>/dev/null || echo 0)
  results=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("results_backfilled",0)) if t else 0)' 2>/dev/null || echo 0)
  status="ok"
  if [ "${orders:-0}" -eq 0 ] || [ "${results:-0}" -eq 0 ]; then
    fail_count=$((fail_count+1))
    status="degraded"
  else
    fail_count=0
  fi
  cat > "$STATUS" <<JSON
{"ts":"$ts","tag":"$tag","strategy":"$STRAT","orders":$orders,"results":$results,"fail_count":$fail_count,"status":"$status"}
JSON
  sleep "$INTERVAL"
done
