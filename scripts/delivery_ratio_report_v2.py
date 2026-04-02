#!/usr/bin/env python3
"""Delivery ratio report v2 (S/A focus + mvc->done conversion).

Reads latest records from REQUIREMENTS_TRIAGED and prints:
- counts by importance and status
- S/A pending+mvcs list
- mvc->done ratio

Usage:
  python3 scripts/delivery_ratio_report_v2.py
"""

import json, os, collections

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
LATEST=os.path.join(ROOT,'data','requirements','requirements_latest.jsonl')
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

if os.path.exists(LATEST):
    path=LATEST
elif os.path.exists(TRI):
    path=TRI
else:
    print('NO_TRIAGED')
    raise SystemExit(0)

rows=[]
latest={}
with open(path,'r',encoding='utf-8') as f:
    for ln in f:
        ln=ln.strip()
        if not ln: continue
        r=json.loads(ln)
        # if using TRI directly, id is unique per line; still keep last occurrence
        latest[r.get('id')]=r
rows=list(latest.values())

by_imp_status=collections.Counter((r.get('importance'), r.get('status')) for r in rows)

print('# Delivery ratio v2')
print('counts (importance,status):')
for k,v in sorted(by_imp_status.items(), key=lambda x:(x[0][0],x[0][1])):
    print(f'- {k}: {v}')

sa=[r for r in rows if r.get('importance') in ('S','A')]
sa_pending=[r for r in sa if r.get('status') in ('pending','mvc')]

mvc=sum(1 for r in sa if r.get('status')=='mvc')
done=sum(1 for r in sa if r.get('status')=='done')
ratio = done / max(1, done+mvc)
print(f"\nS/A mvc={mvc} done={done} mvc_to_done_ratio={ratio:.4f}")

print('\n## S/A not done')
sa_pending.sort(key=lambda r: ({'S':0,'A':1}.get(r.get('importance'),9), r.get('type','')))
for r in sa_pending:
    print(f"- {r.get('importance')} {r.get('type')} {r.get('status')} {r.get('slug','')}: {r.get('text')}")
