#!/usr/bin/env python3
"""Build a stable latest-view of requirements.

Problem: REQUIREMENTS_TRIAGED.jsonl can contain duplicates (multiple ids for same logical req).
This tool groups by `slug` when present; otherwise falls back to id.
Within a group, chooses the record with highest status and newest ts.

Status priority: done > mvc > pending.

Outputs: data/requirements/requirements_latest.jsonl

Usage:
  python3 scripts/req_latest.py
"""

import json, os, datetime

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')
OUT=os.path.join(ROOT,'data','requirements','requirements_latest.jsonl')

os.makedirs(os.path.dirname(OUT), exist_ok=True)

prio={'pending':0,'mvc':1,'done':2}

def key(r):
    return r.get('slug') or r.get('id')

def ts(r):
    return r.get('ts') or ''

latest={}
if os.path.exists(TRI):
    with open(TRI,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            r=json.loads(ln)
            k=key(r)
            cur=latest.get(k)
            if not cur:
                latest[k]=r
                continue
            # compare by status priority then timestamp
            if prio.get(r.get('status','pending'),0) > prio.get(cur.get('status','pending'),0):
                latest[k]=r
            elif prio.get(r.get('status','pending'),0) == prio.get(cur.get('status','pending'),0) and ts(r) > ts(cur):
                latest[k]=r

with open(OUT,'w',encoding='utf-8') as out:
    for r in latest.values():
        out.write(json.dumps(r,ensure_ascii=False)+'\n')

print(OUT)
