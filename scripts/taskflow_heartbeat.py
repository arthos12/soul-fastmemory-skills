#!/usr/bin/env python3
import json, os, time, datetime as dt
from pathlib import Path

OUTDIR = Path('data/taskflow')
OUTDIR.mkdir(parents=True, exist_ok=True)
STATUS = OUTDIR / 'heartbeat_status.json'
LOG = OUTDIR / 'heartbeat_log.jsonl'

while True:
    now = dt.datetime.utcnow().isoformat() + 'Z'
    payload = {'ts': now, 'status': 'alive', 'epoch': int(time.time())}
    STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    with LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False) + '\n')
    time.sleep(30)
