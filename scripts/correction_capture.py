#!/usr/bin/env python3
"""Capture a user correction as a prevention task.

Usage:
  python3 scripts/correction_capture.py --correction "..." --source chat

Effect:
- Adds one S/brain requirement into inbox: "防复发：<correction>"
- Immediately triages and refreshes latest view.
"""

import argparse, subprocess, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

def sh(cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--correction', required=True)
    ap.add_argument('--source', default='chat')
    args=ap.parse_args()

    text=f"防复发：{args.correction.strip()}"
    rid=sh(['python3','scripts/req_add.py','--text',text,'--source',args.source,'--priority','P0'])
    try:
        sh(['python3','scripts/req_triage.py','--limit','50'])
    except Exception:
        pass
    try:
        sh(['python3','scripts/req_latest.py'])
    except Exception:
        pass
    print(rid)

if __name__=='__main__':
    main()
