#!/usr/bin/env python3
"""Model audit auto log.

Goal: every time we run a batch/validation/delivery pipeline, append a structured audit record
of what model/scene/metrics were used, so later we can answer "what model did you use and did it help".

This is a minimal, local-first logger (no network).

It records:
- timestamp
- scene (free text)
- current focus lanes
- recent efficiency snapshot (last line of metrics.jsonl)
- git HEAD (short)

Usage:
  python3 scripts/model_audit_auto_log.py --scene "idle_cycle" --note "optional"

Output:
  data/model_audit/audit.jsonl (append)
"""

import argparse, json, os, subprocess, datetime

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT_DIR=os.path.join(ROOT,'data','model_audit')
OUT=os.path.join(OUT_DIR,'audit.jsonl')
MET=os.path.join(ROOT,'data','efficiency','metrics.jsonl')
FOCUS=os.path.join(ROOT,'tasks','REQUIREMENTS_FOCUS.json')


def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def sh(cmd):
    return subprocess.check_output(['bash','-lc',cmd], cwd=ROOT, text=True).strip()


def read_last_line(path):
    if not os.path.exists(path):
        return None
    last=None
    with open(path,'r',encoding='utf-8') as f:
        for ln in f:
            if ln.strip():
                last=ln
    return last


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scene', required=True)
    ap.add_argument('--note', default='')
    args=ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    focus=None
    if os.path.exists(FOCUS):
        try:
            focus=json.load(open(FOCUS,'r',encoding='utf-8'))
        except Exception:
            focus=None

    last_metrics=read_last_line(MET)
    metrics_obj=None
    if last_metrics:
        try:
            metrics_obj=json.loads(last_metrics)
        except Exception:
            metrics_obj={'raw': last_metrics.strip()}

    head=None
    try:
        head=sh('git rev-parse --short HEAD')
    except Exception:
        head=None

    rec={
        'ts': now(),
        'scene': args.scene,
        'note': args.note,
        'focus': (focus or {}),
        'efficiencyMetricsLast': metrics_obj,
        'gitHead': head,
    }

    with open(OUT,'a',encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False)+'\n')

    # human one-line
    lanes=(rec.get('efficiencyMetricsLast') or {}).get('lanes')
    print(f"MODEL_AUDIT scene={args.scene} git={head} lanes={lanes}")

if __name__=='__main__':
    main()
