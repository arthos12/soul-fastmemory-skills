#!/usr/bin/env python3
"""Add a raw requirement into REQUIREMENTS_INBOX.jsonl.

Usage:
  python3 scripts/req_add.py --text "..." --source chat --priority P2

This is the *intake* stage only (no auto-triage).
"""

import argparse, json, time, datetime, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INBOX = os.path.join(ROOT, 'tasks', 'REQUIREMENTS_INBOX.jsonl')

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'

def slugify(s: str):
    import re
    s=s.lower().strip()
    s=re.sub(r'[^a-z0-9]+','_',s)
    s=re.sub(r'^_+|_+$','',s)
    return s[:48] or 'req'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--source', default='chat')
    ap.add_argument('--priority', default='P2', choices=['P0','P1','P2'])
    args=ap.parse_args()

    os.makedirs(os.path.dirname(INBOX), exist_ok=True)
    # millisecond timestamp to avoid collisions when capturing multiple points in one second
    rid = f"{int(time.time()*1000)}_{slugify(args.text)}"
    rec = {
        'ts': now(),
        'id': rid,
        'text': args.text,
        'source': args.source,
        'priorityHint': args.priority,
        'state': 'inbox'
    }
    with open(INBOX,'a',encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    print(rid)

if __name__=='__main__':
    main()
