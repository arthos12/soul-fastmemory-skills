#!/usr/bin/env python3
"""Report requirements by layer (brain vs business).

Layer mapping:
- type == 'brain' => brain layer
- else => business layer

Usage:
  python3 scripts/layer_report.py
"""

import json, os, collections

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
LATEST=os.path.join(ROOT,'data','requirements','requirements_latest.jsonl')
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

path = LATEST if os.path.exists(LATEST) else TRI
if not os.path.exists(path):
    print('NO_DATA')
    raise SystemExit(0)

rows=[]
latest={}
for ln in open(path,'r',encoding='utf-8'):
    ln=ln.strip()
    if not ln: continue
    r=json.loads(ln)
    latest[r.get('id')]=r
rows=list(latest.values())


def layer(r):
    return 'brain' if r.get('type')=='brain' else 'business'

ctr=collections.Counter((layer(r), r.get('status')) for r in rows if r.get('importance') in ('S','A'))

print('Layer status (S/A):')
for k,v in sorted(ctr.items()):
    print(f'- {k}: {v}')

# list not-done brain first
for lay in ('brain','business'):
    nd=[r for r in rows if r.get('importance') in ('S','A') and layer(r)==lay and r.get('status') in ('pending','mvc')]
    if not nd: continue
    print(f"\n## {lay} not done")
    for r in sorted(nd, key=lambda x:({'S':0,'A':1}.get(x.get('importance'),9), x.get('status',''))):
        print(f"- {r.get('importance')} {r.get('status')} {r.get('slug') or r.get('id')}: {r.get('text')}")
