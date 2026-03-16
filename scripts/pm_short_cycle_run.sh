#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
mkdir -p data/polymarket
TODAY_UTC="$(date -u +%F)"
SRC="data/polymarket/markets_short_${TODAY_UTC}.jsonl"
FILT="data/polymarket/markets_short_filtered_${TODAY_UTC}.jsonl"
PRED="data/polymarket/predictions_short_${TODAY_UTC}.jsonl"
LEDGER="data/polymarket/paper_orders_short_${TODAY_UTC}.jsonl"
python3 scripts/polymarket_pull.py --limit 200 --active 1 --closed 0 --out "$SRC" >/dev/null
python3 - <<'PY'
import json,datetime
utc_day=datetime.datetime.utcnow().date().isoformat()
src='data/polymarket/markets_short_' + utc_day + '.jsonl'
out='data/polymarket/markets_short_filtered_' + utc_day + '.jsonl'
now=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
keep=[]
for line in open(src,encoding='utf-8'):
    if not line.strip(): continue
    r=json.loads(line)
    if r.get('outcomes')!=['Yes','No']: continue
    q=(r.get('question') or '').lower()
    if not any(k in q for k in ['bitcoin','btc','ethereum','eth','up or down','up or','higher','above','below','rise','fall']):
        continue
    try:
        end=datetime.datetime.fromisoformat((r.get('endDate') or '').replace('Z','+00:00'))
    except Exception:
        continue
    hrs=(end-now).total_seconds()/3600
    if 0 < hrs <= 48:
        keep.append(r)
with open(out,'w',encoding='utf-8') as f:
    for r in keep: f.write(json.dumps(r, ensure_ascii=False)+'\n')
print(len(keep))
PY
python3 scripts/polymarket_predict.py --in "$FILT" --out "$PRED" --limit 80 >/dev/null
python3 scripts/polymarket_paper_trade.py --in "$PRED" --out "$LEDGER" --threshold 0.03 --sizing fixed --fixed-stake 1000 >/dev/null
printf 'SRC=%s\nFILT=%s\nPRED=%s\nLEDGER=%s\n' "$SRC" "$FILT" "$PRED" "$LEDGER"
