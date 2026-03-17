#!/usr/bin/env python3
import json, os, glob, time
from pathlib import Path
status_path='data/polymarket/runtime/br_loop_status.json'
out={'status_file_exists': os.path.exists(status_path)}
now=time.time()
if os.path.exists(status_path):
    j=json.load(open(status_path))
    out['status']=j
    # freshness in seconds
    try:
        ts=time.mktime(time.strptime(j['ts'], '%Y-%m-%dT%H:%M:%SZ'))
        out['freshness_sec']=int(now-ts)
        out['fresh']=out['freshness_sec'] <= 900
    except Exception:
        out['fresh']=False
recent=[]
for p in sorted(glob.glob('data/polymarket/paper_orders_2026-03-17_*.jsonl'))[-5:]:
    recent.append({'file':Path(p).name,'mtime':int(os.path.getmtime(p)),'lines':sum(1 for _ in open(p,encoding='utf-8') if _.strip())})
out['recent_orders']=recent
print(json.dumps(out,ensure_ascii=False))
