#!/usr/bin/env python3
"""Triage inbox requirements into TRIAGED.jsonl with classification fields.

Heuristic v0 (fast):
- truth: real/soft/uncertain
- importance: S/A/B
- type: brain/skill/business/system
- status: pending

Usage:
  python3 scripts/req_triage.py --limit 20

Notes:
- Does not delete inbox; it appends triaged entries.
"""

import argparse, json, os, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INBOX = os.path.join(ROOT,'tasks','REQUIREMENTS_INBOX.jsonl')
TRI = os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'

REAL_TRIGGERS = ['马上','执行','落地','必须','要','检查','验收']
SOFT_TRIGGERS = ['感觉','希望','应该','可以试试','聊聊']


def classify(text: str):
    t=text.strip()
    truth='uncertain'
    if any(k in t for k in REAL_TRIGGERS): truth='real'
    if any(k in t for k in SOFT_TRIGGERS) and truth!='real': truth='soft'

    # importance
    imp='B'
    if any(k in t for k in ['效率','主次','主要矛盾','空闲','不依赖会话','自我修复']): imp='S'
    elif any(k in t for k in ['预测','polymarket','监控','gold','silver','A股','lobster']): imp='A'

    # type (layer mapping)
    # brain layer
    typ='business'
    if any(k in t for k in ['大脑','主次','判断','逻辑','理解','自我修复','效率','纠错','不复发','验证','需求系统','去重','同步']):
        typ='brain'
    # business layer (keep skill as business-layer deliverable)
    elif any(k in t.lower() for k in ['polymarket','brier','score','预测']):
        typ='business'
    elif any(k in t for k in ['网关','cron','服务','脚本','模型库','model']):
        # system tasks usually belong to brain layer because they affect execution reliability
        typ='brain'

    return truth, imp, typ


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=50)
    args=ap.parse_args()

    if not os.path.exists(INBOX):
        print('NO_INBOX')
        return

    os.makedirs(os.path.dirname(TRI), exist_ok=True)

    # load already triaged ids (latest view)
    triaged=set()
    if os.path.exists(TRI):
        with open(TRI,'r',encoding='utf-8') as tf:
            for ln in tf:
                ln=ln.strip()
                if not ln: continue
                try:
                    triaged.add(json.loads(ln).get('id'))
                except Exception:
                    pass

    out=[]
    with open(INBOX,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            r=json.loads(line)
            if r.get('state')!='inbox':
                continue
            if r.get('id') in triaged:
                continue
            out.append(r)
            if len(out)>=args.limit: break

    if not out:
        print('NO_PENDING')
        return

    with open(TRI,'a',encoding='utf-8') as f:
        for r in out:
            truth,imp,typ=classify(r.get('text',''))
            rec={
                'ts': now(),
                'id': r.get('id'),
                'text': r.get('text'),
                'source': r.get('source'),
                'truth': truth,
                'importance': imp,
                'type': typ,
                'status': 'pending',
                'depends_on': [],
                'artifacts': []
            }
            f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    print(json.dumps({'triaged': len(out)}, ensure_ascii=False))

if __name__=='__main__':
    main()
