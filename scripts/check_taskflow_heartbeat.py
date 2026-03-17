#!/usr/bin/env python3
import json, os, time
from pathlib import Path
p = Path('data/taskflow/heartbeat_status.json')
out = {'exists': p.exists(), 'now': int(time.time())}
if p.exists():
    j = json.loads(p.read_text(encoding='utf-8'))
    out['status'] = j
    out['age_sec'] = int(time.time()) - int(j.get('epoch', 0))
    out['fresh'] = out['age_sec'] <= 45
print(json.dumps(out, ensure_ascii=False))
