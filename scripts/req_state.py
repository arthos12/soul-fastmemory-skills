#!/usr/bin/env python3
"""Append-only requirement state updates + latest-view utilities.

Commands:
  latest      Print latest records per id (jsonl)
  set-status  Append an update for an id

Usage:
  python3 scripts/req_state.py latest
  python3 scripts/req_state.py set-status --id <id> --status done --artifacts a,b,c
"""

import argparse, json, os, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRI = os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def load_latest():
    latest = {}
    if not os.path.exists(TRI):
        return latest
    with open(TRI,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            r=json.loads(ln)
            rid=r.get('id')
            if rid:
                latest[rid]=r
    return latest


def cmd_latest(_args):
    latest = load_latest()
    for r in latest.values():
        print(json.dumps(r, ensure_ascii=False))


def cmd_set_status(args):
    latest = load_latest().get(args.id)
    if not latest:
        raise SystemExit('UNKNOWN_ID')
    upd = dict(latest)
    upd['ts'] = now()
    upd['status'] = args.status
    if args.artifacts:
        upd['artifacts'] = [a for a in args.artifacts.split(',') if a]
    with open(TRI,'a',encoding='utf-8') as f:
        f.write(json.dumps(upd, ensure_ascii=False)+'\n')
    print('OK')


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('latest')
    sp=sub.add_parser('set-status')
    sp.add_argument('--id', required=True)
    sp.add_argument('--status', required=True, choices=['pending','mvc','done'])
    sp.add_argument('--artifacts', default='')
    args=ap.parse_args()

    if args.cmd=='latest':
        cmd_latest(args)
    elif args.cmd=='set-status':
        cmd_set_status(args)

if __name__=='__main__':
    main()
