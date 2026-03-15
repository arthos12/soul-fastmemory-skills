#!/usr/bin/env python3
"""Run multiple validation commands in parallel and summarize pass/fail.

Usage:
  python3 scripts/parallel_validate.py --cmd "bash scripts/a.sh" --cmd "python3 scripts/b.py" 

Exit code:
- 0 if all pass
- 1 otherwise

Output:
- Prints a short summary with per-command status and tail.
"""

import argparse, subprocess, os, time

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))


def run(cmd):
    start=time.time()
    p=subprocess.Popen(['bash','-lc',cmd], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out,_=p.communicate(timeout=120)
    tail='\n'.join(out.strip().splitlines()[-8:])
    return {'cmd':cmd,'code':p.returncode,'secs':round(time.time()-start,3),'tail':tail}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cmd', action='append', required=True)
    args=ap.parse_args()

    procs=[]
    for c in args.cmd:
        p=subprocess.Popen(['bash','-lc',c], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        procs.append((c,p,time.time()))

    results=[]
    ok=True
    for c,p,st in procs:
        try:
            out,_=p.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            p.kill(); out='TIMEOUT'
        tail='\n'.join(str(out).strip().splitlines()[-8:])
        code=p.returncode if p.returncode is not None else 1
        if code!=0:
            ok=False
        results.append({'cmd':c,'code':code,'secs':round(time.time()-st,3),'tail':tail})

    for r in results:
        status='PASS' if r['code']==0 else 'FAIL'
        print(f"[{status}] {r['secs']}s :: {r['cmd']}")
        if r['tail']:
            print(r['tail'])
            print('---')

    raise SystemExit(0 if ok else 1)

if __name__=='__main__':
    main()
