#!/usr/bin/env python3
"""Sync status between DELIVERY_BACKLOG.md and REQUIREMENTS_TRIAGED.jsonl.

Goal: keep single truth in practice.
- DELIVERY_BACKLOG.md is the human-visible delivery truth for [m]/[x].
- TRIAGED has structured fields used by focus/reporting.

Rule (v1): for any backlog item with slug S:
- map id = backlog_<slug>
- if backlog has [x] -> triaged status = done
- if backlog has [m] -> triaged status = mvc
- if backlog has [ ] -> triaged status = pending

Appends updates to TRIAGED (append-only) using latest record as base.

Usage:
  python3 scripts/req_sync_backlog_status.py
"""

import json, os, re, datetime

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
BACKLOG=os.path.join(ROOT,'tasks','DELIVERY_BACKLOG.md')
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

rx=re.compile(r'^- \[(?P<chk>[ xmx])\] (?P<slug>[a-z0-9_\-]+)\b')

prio={'pending':0,'mvc':1,'done':2}

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def load_latest():
    latest={}
    if not os.path.exists(TRI):
        return latest
    with open(TRI,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            r=json.loads(ln)
            latest[r.get('id')]=r
    return latest


def main():
    if not os.path.exists(BACKLOG):
        print('NO_BACKLOG')
        return

    latest=load_latest()

    # parse backlog desired statuses
    desired={}
    for ln in open(BACKLOG,'r',encoding='utf-8'):
        m=rx.match(ln.strip())
        if not m: continue
        chk=m.group('chk')
        slug=m.group('slug')
        if chk=='x': st='done'
        elif chk=='m': st='mvc'
        else: st='pending'
        rid=f'backlog_{slug}'
        desired[rid]=st

    updates=[]
    for rid,st in desired.items():
        cur=latest.get(rid)
        if not cur:
            # create minimal record if missing
            cur={'id':rid,'text':slug,'source':'backlog','truth':'real','importance':'A','type':'business','status':'pending','depends_on':[],'artifacts':[]}
        if cur.get('status')==st:
            continue
        upd=dict(cur)
        upd['ts']=now()
        upd['status']=st
        updates.append(upd)

    if not updates:
        print('NO_CHANGES')
        return

    with open(TRI,'a',encoding='utf-8') as f:
        for u in updates:
            f.write(json.dumps(u,ensure_ascii=False)+'\n')

    print(json.dumps({'updated':len(updates)},ensure_ascii=False))

if __name__=='__main__':
    main()
