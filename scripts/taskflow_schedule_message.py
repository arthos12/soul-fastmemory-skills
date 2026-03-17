#!/usr/bin/env python3
import json, os, sys, time, datetime as dt
from pathlib import Path

OUT = Path('data/taskflow')
OUT.mkdir(parents=True, exist_ok=True)
msg = {
  'ts': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
  'kind': 'scheduled_message',
  'message': 'TaskFlow scheduled checkpoint reached. Review data/taskflow/scheduled_report.json and data/polymarket/runtime/br_loop_status.json.'
}
(OUT / 'outbox_latest.json').write_text(json.dumps(msg, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(msg, ensure_ascii=False))
