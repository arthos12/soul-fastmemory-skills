#!/usr/bin/env python3
import json, os, time, glob
from pathlib import Path
out = {}
# taskflow heartbeat
p = Path('data/taskflow/heartbeat_status.json')
out['taskflow_heartbeat_exists'] = p.exists()
if p.exists():
    j = json.loads(p.read_text(encoding='utf-8'))
    out['taskflow_heartbeat'] = j
    out['taskflow_age_sec'] = int(time.time()) - int(j.get('epoch', 0))
# dual monitor
p2 = Path('data/polymarket/runtime/dual_side_monitor_status.json')
out['dual_monitor_exists'] = p2.exists()
if p2.exists():
    out['dual_monitor'] = json.loads(p2.read_text(encoding='utf-8'))
# br runtime
p3 = Path('data/polymarket/runtime/br_loop_status.json')
out['br_runtime_exists'] = p3.exists()
if p3.exists():
    out['br_runtime'] = json.loads(p3.read_text(encoding='utf-8'))
# latest orders/results counts
for kind in ['paper_orders','paper_results']:
    files=sorted(glob.glob(f'data/polymarket/{kind}_2026-03-17_*.jsonl'), key=os.path.getmtime, reverse=True)[:3]
    out[kind]=[]
    for fp in files:
        lines=sum(1 for _ in open(fp,encoding='utf-8') if _.strip())
        out[kind].append({'file': os.path.basename(fp), 'lines': lines, 'mtime': int(os.path.getmtime(fp))})
Path('data/taskflow/once_report.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False))
