#!/usr/bin/env python3
"""Print a concise S/A completion snapshot and mark it delivered.

Usage:
  python3 scripts/req_ratio_snapshot.py --report-id <id>

Writes marker to: data/efficiency/report_marks.jsonl
"""

import argparse, json, os, datetime

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
MARK=os.path.join(ROOT,'data','efficiency','report_marks.jsonl')
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')
LATEST=os.path.join(ROOT,'data','requirements','requirements_latest.jsonl')


def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def load_rows(path):
    rows=[]
    if not os.path.exists(path):
        return rows
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--report-id', required=True)
    args=ap.parse_args()

    path = LATEST if os.path.exists(LATEST) else TRI
    rows = load_rows(path)

    sa=[r for r in rows if r.get('importance') in ('S','A')]
    mvc=sum(1 for r in sa if r.get('status')=='mvc')
    done=sum(1 for r in sa if r.get('status')=='done')
    ratio = done / max(1, done+mvc)

    print(f"S/A: done={done} mvc={mvc} ratio={ratio:.4f}")

    os.makedirs(os.path.dirname(MARK), exist_ok=True)
    with open(MARK,'a',encoding='utf-8') as f:
        f.write(json.dumps({'ts': now(), 'reportId': args.report_id, 'done': done, 'mvc': mvc, 'ratio': ratio}, ensure_ascii=False)+'\n')


if __name__=='__main__':
    main()
