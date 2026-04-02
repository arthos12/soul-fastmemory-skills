#!/usr/bin/env python3
import argparse, time, json, datetime as dt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--delay-sec', type=int, required=True)
ap.add_argument('--message', required=True)
args = ap.parse_args()

out = Path('data/taskflow')
out.mkdir(parents=True, exist_ok=True)
status = out / 'delayed_send_status.json'
status.write_text(json.dumps({
    'ts': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'status': 'sleeping',
    'delaySec': args.delay_sec,
    'message': args.message,
}, ensure_ascii=False, indent=2), encoding='utf-8')

time.sleep(args.delay_sec)

status.write_text(json.dumps({
    'ts': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'status': 'ready_to_send',
    'message': args.message,
}, ensure_ascii=False, indent=2), encoding='utf-8')

print(args.message)
