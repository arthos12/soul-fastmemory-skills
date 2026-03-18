#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
STRAT="${1:-strategies/br_v2_highprob.json}"
INTERVAL="${2:-600}"
STATUS="data/polymarket/runtime/auto_loop_status.json"
TUNE_LOG="data/polymarket/runtime/auto_tune.jsonl"
mkdir -p data/polymarket/runtime

apply_tune() {
  local reason="$1"
  python3 - <<'PY'
import json,sys,os
path=os.environ['STRAT']
reason=os.environ['REASON']
with open(path,'r',encoding='utf-8') as f:
    s=json.load(f)
changed=False
# auto relax minPrice down to 0.5
mp=float(s.get('minPrice',0.7))
if mp>0.5:
    s['minPrice']=round(max(0.5, mp-0.02),4)
    changed=True
# auto widen maxMinsToEnd up to 525600
mm=int(s.get('maxMinsToEnd',1440))
if mm<525600:
    s['maxMinsToEnd']=min(525600, int(mm*1.5))
    changed=True
if changed:
    with open(path,'w',encoding='utf-8') as f:
        json.dump(s,f,ensure_ascii=False,indent=2)
print(json.dumps({"changed":changed,"minPrice":s.get('minPrice'),"maxMinsToEnd":s.get('maxMinsToEnd'),"reason":reason}))
PY
}

while true; do
  ts=$(date -u +%FT%TZ)
  # guard check
  scripts/system_protection_guard.sh >/dev/null 2>&1 || true
  if [[ -f data/system_guard/guard.flag ]]; then
    echo "{\"ts\":\"$ts\",\"status\":\"paused_guard\"}" > "$STATUS"
    sleep "$INTERVAL"
    continue
  fi

  tag="auto_$(date -u +%H%M%S)"
  out=$(python3 scripts/pm_paper_loop.py --strategy "$STRAT" --tag "$tag" --scan-pages 25 --cache-age-sec 120 || true)
  orders=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("orders_generated",0)) if t else 0)' 2>/dev/null || echo 0)
  results=$(printf '%s' "$out" | python3 -c 'import sys,json; t=sys.stdin.read().strip(); print((json.loads(t).get("results_backfilled",0)) if t else 0)' 2>/dev/null || echo 0)
  echo "$out" > "$STATUS"

  if [[ "${orders:-0}" -eq 0 ]]; then
    export STRAT REASON
    REASON="orders_zero"
    tune=$(apply_tune "$REASON")
    echo "{\"ts\":\"$ts\",\"reason\":\"$REASON\",\"tune\":$tune}" >> "$TUNE_LOG"
  fi
  sleep "$INTERVAL"
done
