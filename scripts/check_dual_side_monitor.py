#!/usr/bin/env python3
import json, os, time
path='data/polymarket/runtime/dual_side_monitor_status.json'
out={'exists': os.path.exists(path), 'now': int(time.time())}
if os.path.exists(path):
    with open(path,'r',encoding='utf-8') as f:
        out['status']=json.load(f)
print(json.dumps(out, ensure_ascii=False))
