#!/usr/bin/env python3
"""Capture multi-point user message into REQUIREMENTS_INBOX, then triage.

Usage:
  python3 scripts/conv_req_capture.py --text "..." [--source chat] [--priority P0]

Heuristic split: newlines, ';', '；', '。', '，' when list-like. Keeps only non-empty.
Outputs JSON: {added:[ids], count:n}
"""

import argparse, json, re, subprocess, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

def split_points(text:str):
    t=text.strip()
    if not t:
        return []
    # Normalize
    t=t.replace('\r\n','\n').replace('\r','\n')
    # If looks like list (multiple separators/newlines), split; else keep whole
    seps = ['\n',';','；','。']
    if sum(t.count(s) for s in seps) >= 2:
        parts=re.split(r"\n+|[;；]+|[。]+", t)
    else:
        parts=[t]
    # Further split long parts by '，' only if still clearly multi-point
    out=[]
    for p in parts:
        p=p.strip(' \t-—•*')
        if not p:
            continue
        if len(p)>80 and p.count('，')>=2:
            out.extend([x.strip(' \t-—•*') for x in p.split('，') if x.strip(' \t-—•*')])
        else:
            out.append(p)
    # de-dupe exact
    seen=set(); res=[]
    for p in out:
        if p in seen: continue
        seen.add(p); res.append(p)
    return res


def run(cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--text', required=True)
    ap.add_argument('--source', default='chat')
    ap.add_argument('--priority', default='P0')
    args=ap.parse_args()

    points=split_points(args.text)
    added=[]
    for p in points:
        rid=run(['python3','scripts/req_add.py','--text',p,'--source',args.source,'--priority',args.priority])
        added.append(rid)

    # triage immediately
    try:
        run(['python3','scripts/req_triage.py','--limit','50'])
    except Exception:
        pass
    try:
        run(['python3','scripts/req_latest.py'])
    except Exception:
        pass

    print(json.dumps({'count': len(added), 'added': added}, ensure_ascii=False))

if __name__=='__main__':
    main()
