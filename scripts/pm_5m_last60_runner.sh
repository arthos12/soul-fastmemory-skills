#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
LOG=/tmp/pm_5m_runner.log

while true; do
  server_ts=$(python3 - <<'PY'
import requests
j=requests.get('https://clob.polymarket.com/time',timeout=10).json()
if isinstance(j,dict):
    print(int(j.get('server_time') or j.get('serverTime') or j.get('time') or 0))
else:
    print(int(j))
PY
)
  period=$((server_ts/300*300))
  slug="btc-updown-5m-${period}"
  secs=$(python3 - <<PY
import requests,datetime
m=requests.get('https://polymarket.com/api/market',params={'slug':'$slug'},timeout=10).json()
end_raw=m.get('endDate')
if not end_raw:
    print(9999)
else:
    end=datetime.datetime.fromisoformat(end_raw.replace('Z','+00:00'))
    print(int(end.timestamp())-$server_ts)
PY
)
  # only log during matching window

  if [ "$secs" -le 20 ]; then
    # log every tick within last 60s window
    prices=$(python3 - <<PY
import requests
m=requests.get('https://polymarket.com/api/market',params={'slug':'$slug'},timeout=10).json()
print(m.get('outcomePrices'))
PY
)
    echo "$(date -u +%FT%TZ) server_ts=$server_ts secs_to_end=$secs prices=$prices" >> "$LOG"
    python3 - <<PY
import json,time
from pathlib import Path
log=Path('/root/.openclaw/workspace/data/polymarket/runtime/last20_window.jsonl')
log.parent.mkdir(parents=True,exist_ok=True)
with log.open('a',encoding='utf-8') as f:
    f.write(json.dumps({"ts": int(time.time()), "secsToEnd": $secs, "prices": $prices, "slug": "$slug"}, ensure_ascii=False) + "\n")
PY
    # run must-hit strategies first
    for f in /root/.openclaw/workspace/strategies/pm_5m_t60_p051.json /root/.openclaw/workspace/strategies/pm_5m_t60_p049_low.json; do
      tag=$(basename "$f" .json)
      python3 /root/.openclaw/workspace/scripts/pm_paper_loop.py --strategy "$f" --tag "$tag" --scan-pages 1 --cache-age-sec 3 >> "$LOG" 2>&1 || true
    done
    # then run full set
    for f in /root/.openclaw/workspace/strategies/pm_5m_*.json; do
      tag=$(basename "$f" .json)
      python3 /root/.openclaw/workspace/scripts/pm_paper_loop.py --strategy "$f" --tag "$tag" --scan-pages 1 --cache-age-sec 3 >> "$LOG" 2>&1 || true
    done
  fi
  sleep 1
  done
