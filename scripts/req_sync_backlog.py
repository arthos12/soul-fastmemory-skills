#!/usr/bin/env python3
"""Sync DELIVERY_BACKLOG.md (P0/P1/P2) into REQUIREMENTS_INBOX+TRIAGED.

Goal: avoid context mixing and keep a single truth in structured form.

This is a one-way sync (md -> jsonl) for now.

Usage:
  python3 scripts/req_sync_backlog.py
"""

import os, re, json, datetime, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MD = os.path.join(ROOT, 'tasks', 'DELIVERY_BACKLOG.md')
INBOX = os.path.join(ROOT, 'tasks', 'REQUIREMENTS_INBOX.jsonl')
TRI = os.path.join(ROOT, 'tasks', 'REQUIREMENTS_TRIAGED.jsonl')


def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def slugify(s: str):
    s=s.lower().strip()
    s=re.sub(r'[^a-z0-9]+','_',s)
    s=re.sub(r'^_+|_+$','',s)
    return s[:48] or 'req'


def main():
    if not os.path.exists(MD):
        print('NO_MD')
        return
    os.makedirs(os.path.dirname(INBOX), exist_ok=True)

    # load already triaged ids to avoid dup
    seen=set()
    for path in (TRI,):
        if os.path.exists(path):
            with open(path,'r',encoding='utf-8') as f:
                for ln in f:
                    ln=ln.strip()
                    if not ln: continue
                    try:
                        seen.add(json.loads(ln).get('id'))
                    except Exception:
                        pass

    sec=None
    added=0
    with open(MD,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.rstrip('\n')
            if ln.startswith('## '):
                sec=ln.replace('## ','').strip().split('（')[0]
                continue
            m=re.match(r'^- \[( |m|x)\] ([a-z0-9_\-]+) - (.*)$', ln)
            if not m:
                continue
            state=m.group(1)
            slug=m.group(2)
            text=m.group(3)
            # deterministic id to avoid duplication across sync runs
            rid=f"backlog_{slug}"
            if rid in seen:
                continue
            # map section to priority hint
            pr='P2'
            if sec and sec.startswith('P0'): pr='P0'
            elif sec and sec.startswith('P1'): pr='P1'
            # inbox
            inbox_rec={
                'ts': now(),
                'id': rid,
                'text': text,
                'source': 'delivery_backlog',
                'priorityHint': pr,
                'state': 'inbox'
            }
            with open(INBOX,'a',encoding='utf-8') as out:
                out.write(json.dumps(inbox_rec,ensure_ascii=False)+"\n")

            # triage quick classification
            truth='real'
            imp='A' if pr!='P0' else 'S'
            typ='business'
            if pr=='P0': typ='brain'
            elif 'polymarket' in text.lower() or 'brier' in text.lower() or '预测' in text: typ='skill'

            status='pending'
            if state=='m': status='mvc'
            if state=='x': status='done'

            tri_rec={
                'ts': now(),
                'id': rid,
                'slug': slug,
                'text': text,
                'source': 'delivery_backlog',
                'truth': truth,
                'importance': imp,
                'type': typ,
                'status': status,
                'depends_on': [],
                'artifacts': []
            }
            with open(TRI,'a',encoding='utf-8') as out:
                out.write(json.dumps(tri_rec,ensure_ascii=False)+"\n")
            added+=1

    print(json.dumps({'added': added}, ensure_ascii=False))


if __name__=='__main__':
    main()
