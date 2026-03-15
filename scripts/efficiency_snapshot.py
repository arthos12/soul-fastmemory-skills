#!/usr/bin/env python3
"""Efficiency snapshot (human-first).

Outputs a concise snapshot using the EFF0 library terms:
- Direction proxy: focus lanes count + whether S_brain_not_done blocks others
- Utilization proxy: sum(totalSecs)/wall in last N metrics
- Throughput: deltaBacklogDone in window + current done ratio

Usage:
  python3 scripts/efficiency_snapshot.py --minutes 30
"""

import argparse, json, datetime, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
MET=os.path.join(ROOT,'data','efficiency','metrics.jsonl')

FMT='%Y-%m-%dT%H:%M:%SZ'

def load():
    if not os.path.exists(MET):
        return []
    rows=[]
    with open(MET,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                rows.append(json.loads(ln))
    for r in rows:
        try:
            r['_t']=datetime.datetime.strptime(r['ts'],FMT)
        except Exception:
            r['_t']=None
    return [r for r in rows if r.get('_t')]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--minutes', type=int, default=30)
    args=ap.parse_args()

    rows=load()
    if not rows:
        print('NO_METRICS')
        return

    cutoff=rows[-1]['_t']-datetime.timedelta(minutes=args.minutes)
    win=[r for r in rows if r['_t']>=cutoff]
    if len(win)<2:
        win=rows[-min(len(rows),30):]

    wall=(win[-1]['_t']-win[0]['_t']).total_seconds() or 1.0
    active=sum(float(r.get('totalSecs',0)) for r in win)
    util=active/wall

    delta_done=sum(int(r.get('deltaBacklogDone',0)) for r in win)
    last=win[-1]
    done=int(last.get('backlogDone',0))
    mvc=int(last.get('backlogMVC',0))
    ratio=done/max(1,done+mvc)

    avg_lanes=sum(len(r.get('lanes',[])) for r in win)/len(win)

    print(f"过去{args.minutes}分钟：并发(平均lane数)≈{avg_lanes:.2f}；时间利用率≈{util*100:.1f}%；done增量={delta_done}；当前完成占比={ratio*100:.2f}% ({done}/({done}+{mvc}))")

if __name__=='__main__':
    main()
