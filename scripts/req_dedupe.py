#!/usr/bin/env python3
"""Deduplicate requirements by normalized text and suggest merges.

Outputs a JSON report with groups of duplicate texts.
"""

import json, os, re, hashlib

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')
OUT=os.path.join(ROOT,'data','requirements','dedupe_report.json')

os.makedirs(os.path.dirname(OUT), exist_ok=True)

rx_space=re.compile(r'\s+')

def norm(s:str)->str:
    s=s.strip().lower()
    s=rx_space.sub(' ',s)
    return s

latest={}
if os.path.exists(TRI):
    with open(TRI,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            r=json.loads(ln)
            latest[r.get('id')]=r

by_hash={}
for r in latest.values():
    t=norm(r.get('text',''))
    h=hashlib.sha1(t.encode('utf-8')).hexdigest()[:12]
    by_hash.setdefault(h,[]).append(r)

dups={h:rs for h,rs in by_hash.items() if len(rs)>1}
report={
  'total': len(latest),
  'dupGroups': len(dups),
  'groups': {
    h: [{k:r.get(k) for k in ('id','importance','type','status','text')} for r in rs]
    for h,rs in dups.items()
  }
}
open(OUT,'w',encoding='utf-8').write(json.dumps(report,ensure_ascii=False,indent=2))
print(OUT)
