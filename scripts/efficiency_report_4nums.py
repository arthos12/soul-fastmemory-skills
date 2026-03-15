#!/usr/bin/env python3
"""Human-first efficiency report (4 numbers) for delivery efficiency.

Outputs exactly the four items Jim asked for:
1) concurrency (avg lanes)
2) utilization (active_exec_time / wall_time)
3) idle/empty time estimate
4) done delta + completion ratio (done/(done+mvc))

By default uses the most recent N metrics records (no fixed time window).

Usage:
  python3 scripts/efficiency_report_4nums.py --last-n 30
"""

import argparse, json, datetime, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
MET=os.path.join(ROOT,'data','efficiency','metrics.jsonl')
FMT='%Y-%m-%dT%H:%M:%SZ'


def load_rows():
    if not os.path.exists(MET):
        return []
    rows=[]
    with open(MET,'r',encoding='utf-8') as f:
        for ln in f:
            ln=ln.strip()
            if ln:
                try:
                    r=json.loads(ln)
                    r['_t']=datetime.datetime.strptime(r['ts'],FMT)
                    rows.append(r)
                except Exception:
                    pass
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--last-n', type=int, default=30)
    args=ap.parse_args()

    rows=load_rows()
    if len(rows)<2:
        print('NO_METRICS')
        return

    win=rows[-min(len(rows), args.last_n):]
    wall=(win[-1]['_t']-win[0]['_t']).total_seconds() or 1.0
    active=sum(float(r.get('totalSecs',0)) for r in win)
    util=active/wall
    idle=max(0.0, wall-active)

    avg_lanes=sum(len(r.get('lanes',[])) for r in win)/len(win)
    delta_done=sum(int(r.get('deltaBacklogDone',0)) for r in win)

    last=win[-1]
    done=int(last.get('backlogDone',0))
    mvc=int(last.get('backlogMVC',0))
    ratio=done/max(1,done+mvc)

    # Human-first output (single line)
    print(
        f"并发≈{avg_lanes:.2f}条线；时间利用率≈{util*100:.1f}%；空转≈{idle/60:.1f}分钟；完成：done增量={delta_done}，完成占比={ratio*100:.2f}% ({done}/({done}+{mvc}))"
    )

if __name__=='__main__':
    main()
