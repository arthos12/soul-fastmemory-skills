#!/usr/bin/env python3
import json, os, subprocess, time, datetime as dt
from pathlib import Path

ROOT = Path('.')
OUT = ROOT / 'data/taskflow'
OUT.mkdir(parents=True, exist_ok=True)
STATUS = OUT / 'runner_status.json'
REPORT = OUT / 'scheduled_report.json'
CONFIG = OUT / 'tasks.json'

DEFAULT_TASKS = [
  {"name":"heartbeat","intervalSec":30,"kind":"python","command":["python3","scripts/taskflow_once_report.py"]},
  {"name":"br_runtime_check","intervalSec":60,"kind":"python","command":["python3","scripts/check_br_runtime.py"]}
]

if not CONFIG.exists():
    CONFIG.write_text(json.dumps(DEFAULT_TASKS, ensure_ascii=False, indent=2), encoding='utf-8')

last_run = {}
while True:
    now = int(time.time())
    tasks = json.loads(CONFIG.read_text(encoding='utf-8'))
    summary = {"ts": dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), "tasks": []}
    for t in tasks:
        name = t['name']
        iv = int(t['intervalSec'])
        if now - last_run.get(name, 0) < iv:
            continue
        started = time.time()
        rc = 999
        out = ''
        err = ''
        try:
            p = subprocess.run(t['command'], capture_output=True, text=True, timeout=min(max(iv, 10), 120))
            rc = p.returncode
            out = (p.stdout or '')[-2000:]
            err = (p.stderr or '')[-1000:]
        except Exception as e:
            err = repr(e)
        last_run[name] = now
        summary['tasks'].append({
            'name': name,
            'intervalSec': iv,
            'rc': rc,
            'out': out,
            'err': err,
            'durationMs': int((time.time()-started)*1000)
        })
    STATUS.write_text(json.dumps({"ts": summary['ts'], "lastRun": last_run, "recent": summary['tasks']}, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    time.sleep(5)
