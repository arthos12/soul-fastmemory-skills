#!/usr/bin/env python3
import json, os, time, datetime as dt
from pathlib import Path

from pm_paper_loop import backfill_results, summarize

ORDERS_PATH = 'data/polymarket/verification_dual_orders_manual.jsonl'
OUTDIR = 'data/polymarket/runtime'
STATUS_PATH = os.path.join(OUTDIR, 'dual_side_monitor_status.json')
RESULTS_PATH = 'data/polymarket/verification_dual_results_manual.jsonl'
REPORT_PATH = 'data/polymarket/verification_dual_report.json'


def load_orders(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_results(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    if not os.path.exists(ORDERS_PATH):
        dump_json(STATUS_PATH, {'status':'error','reason':'orders_missing','ts':dt.datetime.utcnow().isoformat()+'Z'})
        return

    orders = load_orders(ORDERS_PATH)
    start = time.time()
    deadline = start + 900  # 15 min cap
    poll_sec = 30

    while True:
        results = backfill_results(orders, tag='dual_live_test_monitor')
        append_results(RESULTS_PATH, results)
        report = summarize(results)
        realized = [r for r in results if r.get('kind') == 'realized']
        side_map = {r.get('picked'): r for r in results}
        passed = False
        reason = 'waiting_terminal'
        if len(realized) >= 2:
            yes = side_map.get('Yes')
            no = side_map.get('No')
            if yes and no and yes.get('winFlag') is not None and no.get('winFlag') is not None:
                passed = (yes.get('winFlag') != no.get('winFlag'))
                reason = 'passed' if passed else 'terminal_but_same_side_result'
        status = {
            'ts': dt.datetime.utcnow().isoformat() + 'Z',
            'status': 'passed' if passed else 'running',
            'reason': reason,
            'report': report,
            'realized_count': len(realized),
            'results_path': RESULTS_PATH,
            'report_path': REPORT_PATH,
        }
        dump_json(STATUS_PATH, status)
        dump_json(REPORT_PATH, {'status': status, 'results': results})
        if passed:
            break
        if time.time() >= deadline:
            status['status'] = 'timeout'
            status['reason'] = reason
            dump_json(STATUS_PATH, status)
            dump_json(REPORT_PATH, {'status': status, 'results': results})
            break
        time.sleep(poll_sec)


if __name__ == '__main__':
    main()
