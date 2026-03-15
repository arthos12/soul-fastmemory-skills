#!/usr/bin/env python3
"""Compute dynamic focus (allowed lanes) from current requirement state + progress signals.

Outputs: tasks/REQUIREMENTS_FOCUS.json

Rules (minimal v1):
- If any S+brain requirement is not done -> focus P0_brain only.
- Else if delivery is stalled (last N metrics deltaBacklogDone==0) -> focus P0_brain only.
- Else -> allow P0_brain + P1_polymarket (keep P2_business off by default).

Usage:
  python3 scripts/req_latest.py >/dev/null && python3 scripts/req_focus.py
"""

import json, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
LATEST=os.path.join(ROOT,'data','requirements','requirements_latest.jsonl')
TRI=os.path.join(ROOT,'tasks','REQUIREMENTS_TRIAGED.jsonl')
METRICS=os.path.join(ROOT,'data','efficiency','metrics.jsonl')
OUT=os.path.join(ROOT,'tasks','REQUIREMENTS_FOCUS.json')


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    return rows


def main():
    rows = load_jsonl(LATEST) or load_jsonl(TRI)
    s_brain_not_done=[r for r in rows if r.get('importance')=='S' and r.get('type')=='brain' and r.get('status')!='done']

    # stall detector
    stall_n=3
    stalled=False
    if os.path.exists(METRICS):
        last=load_jsonl(METRICS)[-stall_n:]
        if last and all(int(r.get('deltaBacklogDone',0))==0 for r in last):
            stalled=True

    # Two-layer rule: if any brain-layer requirement not done, freeze business lanes; run only P0 (delivery+validation)
    if s_brain_not_done:
        allowed=['P0_brain','P0_validate']
        reason='brain_layer_not_done'
    elif stalled:
        allowed=['P0_brain','P0_validate']
        reason=f'stalled_deltaBacklogDone_0_x{stall_n}'
    else:
        # brain layer done: still keep P0 lanes enabled by default; business lanes can be enabled manually later
        allowed=['P0_brain','P0_validate']
        reason='brain_layer_done_default_p0_only'

    out={
        'version': 1,
        'allowedLanes': allowed,
        'reason': reason,
        'sBrainNotDone': [ {'id':r.get('id'), 'slug':r.get('slug'), 'status':r.get('status'), 'text':r.get('text')} for r in s_brain_not_done[:10] ],
    }

    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print(OUT)


if __name__=='__main__':
    main()
