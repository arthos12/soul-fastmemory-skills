#!/usr/bin/env python3
"""Requirement delivery report.

Counts triaged requirements by status/importance/type and prints top pending S/A.

Usage:
  python3 scripts/req_report.py
"""

import json, os, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRI = os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

if not os.path.exists(TRI):
    print('NO_TRIAGED')
    raise SystemExit(0)

rows=[]
with open(TRI,'r',encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if not line: continue
        rows.append(json.loads(line))

by_status=collections.Counter(r.get('status') for r in rows)
by_imp=collections.Counter(r.get('importance') for r in rows)
by_type=collections.Counter(r.get('type') for r in rows)

print('# Requirement report')
print('status:', dict(by_status))
print('importance:', dict(by_imp))
print('type:', dict(by_type))

pending=[r for r in rows if r.get('status')=='pending']
pending.sort(key=lambda r: ( {'S':0,'A':1,'B':2}.get(r.get('importance','B'),3) ))
print('\n## top pending')
for r in pending[:10]:
    print(f"- {r.get('importance')} {r.get('type')} {r.get('id')}: {r.get('text')}")
