#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
STRAT="${1:-strategies/cex_btc_5m_breakout_v1.json}"
TAG="${2:-cex_auto}"
INTERVAL="${3:-900}"
STATUS="data/cex/runtime/${TAG}_status.json"
mkdir -p data/cex/runtime

while true; do
  ts=$(date -u +%FT%TZ)
  scripts/system_protection_guard.sh >/dev/null 2>&1 || true
  if [[ -f data/system_guard/guard.flag ]]; then
    echo "{\"ts\":\"$ts\",\"status\":\"paused_guard\"}" > "$STATUS"
    sleep "$INTERVAL"
    continue
  fi
  out=$(python3 scripts/cex_paper_loop.py --strategy "$STRAT" --outdir data/cex --tag "$TAG" || true)
  echo "$out" > "$STATUS"
  sleep "$INTERVAL"
done
