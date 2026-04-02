#!/usr/bin/env python3
import argparse, datetime as dt, json, os, subprocess, time
from collections import defaultdict

MAINLINE_TASK = 'multi_strategy_engine'


def guard_call(args):
    p = subprocess.run(['python3', 'scripts/execution_guard.py', *args], capture_output=True, text=True)
    return p.stdout.strip()


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def summarize_rows(rows):
    out = {"n": len(rows), "realized_n": 0, "m2m_n": 0, "winrate_realized": None, "roi_avg_realized": None, "roi_avg_m2m": None, "pnl_sum_realized": None, "pnl_sum_m2m": None, "max_drawdown_proxy": None}
    realized = [r for r in rows if r.get('kind') == 'realized']
    m2m = [r for r in rows if r.get('kind') == 'm2m']
    out['realized_n'] = len(realized)
    out['m2m_n'] = len(m2m)

    def avg(nums):
        return sum(nums) / len(nums) if nums else None

    if realized:
        wins = [r for r in realized if r.get('winFlag') is True]
        out['winrate_realized'] = len(wins) / len(realized)
        rois = [float(r['roi_est']) for r in realized if isinstance(r.get('roi_est'), (int, float))]
        pnls = [float(r['pnl_est']) for r in realized if isinstance(r.get('pnl_est'), (int, float))]
        out['roi_avg_realized'] = avg(rois)
        out['pnl_sum_realized'] = sum(pnls) if pnls else None

    if m2m:
        rois = [float(r['roi_est']) for r in m2m if isinstance(r.get('roi_est'), (int, float))]
        pnls = [float(r['pnl_est']) for r in m2m if isinstance(r.get('pnl_est'), (int, float))]
        out['roi_avg_m2m'] = avg(rois)
        out['pnl_sum_m2m'] = sum(pnls) if pnls else None

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in sorted(rows, key=lambda x: x.get('ts_checked', 0)):
        pnl = r.get('pnl_est')
        if not isinstance(pnl, (int, float)):
            continue
        equity += pnl
        peak = max(peak, equity)
        dd = peak - equity
        max_dd = max(max_dd, dd)
    out['max_drawdown_proxy'] = max_dd
    return out


def run_pm(entry):
    cmd = [
        'python3', 'scripts/pm_paper_loop.py',
        '--strategy', entry['strategyPath'],
        '--outdir', entry.get('outdir', 'data/polymarket'),
        '--tag', entry['tag'],
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'ok': p.returncode == 0,
        'cmd': cmd,
        'stdout': p.stdout.strip(),
        'stderr': p.stderr.strip(),
    }


def summarize_pm(entry):
    day = dt.datetime.utcnow().date().isoformat()
    outdir = entry.get('outdir', 'data/polymarket')
    result_path = os.path.join(outdir, f"paper_results_{day}_{entry['tag']}.jsonl")
    rows = read_jsonl(result_path)
    return {
        'resultPath': result_path,
        'summary': summarize_rows(rows),
    }


def run_cex(entry):
    cmd = [
        'python3', 'scripts/cex_paper_loop.py',
        '--strategy', entry['strategyPath'],
        '--klines', entry.get('klinesPath', 'data/cex/binance_btcusdt_5m.json'),
        '--outdir', entry.get('outdir', 'data/cex'),
        '--tag', entry['id'],
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'ok': p.returncode == 0,
        'cmd': cmd,
        'stdout': p.stdout.strip(),
        'stderr': p.stderr.strip(),
    }


def summarize_cex(entry):
    day = dt.datetime.utcnow().date().isoformat()
    outdir = entry.get('outdir', 'data/cex')
    result_path = os.path.join(outdir, f"paper_results_{day}_{entry['id']}.jsonl")
    rows = read_jsonl(result_path)
    normalized = []
    for r in rows:
        normalized.append({
            'kind': r.get('kind', 'realized'),
            'winFlag': r.get('winFlag'),
            'roi_est': r.get('net_ret'),
            'pnl_est': r.get('net_ret'),
            'ts_checked': r.get('ts', 0),
        })
    base = summarize_rows(normalized)
    base['feeBps'] = entry.get('feeBps')
    base['slippageBps'] = entry.get('slippageBps')
    return {
        'resultPath': result_path,
        'summary': base,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default='strategies/strategy_registry.json')
    ap.add_argument('--out', default='data/strategy_hub/latest_run.json')
    args = ap.parse_args()

    reg = load_json(args.registry, default={}) or {}
    strategies = reg.get('strategies', [])
    ts = int(time.time())
    results = []
    grouped = defaultdict(list)

    guard_call(['start-mainline', '--task', MAINLINE_TASK])
    guard_call(['record-progress', '--task', MAINLINE_TASK, '--artifact', 'strategies/strategy_registry.json', '--note', 'runner started'])

    for entry in strategies:
        if not entry.get('enabled', True):
            continue
        kind = entry.get('kind')
        if kind == 'pm_paper':
            run_info = run_pm(entry)
            summary = summarize_pm(entry)
            rec = {'id': entry['id'], 'kind': kind, 'run': run_info, **summary}
        elif kind == 'cex_paper':
            run_info = run_cex(entry)
            summary = summarize_cex(entry)
            rec = {'id': entry['id'], 'kind': kind, 'run': run_info, **summary}
        else:
            rec = {'id': entry.get('id'), 'kind': kind, 'run': {'ok': False, 'error': 'unknown kind'}}
        results.append(rec)
        grouped[kind].append(rec)

    dashboard = {
        'ts': ts,
        'registry': args.registry,
        'strategies_run': len(results),
        'results': results,
    }
    dump_json(args.out, dashboard)
    hist = os.path.join(os.path.dirname(args.out), 'history', f"run_{dt.datetime.utcnow().strftime('%Y-%m-%d_%H%M%S')}.json")
    dump_json(hist, dashboard)
    guard_call(['record-progress', '--task', MAINLINE_TASK, '--artifact', args.out, '--note', 'dashboard updated'])
    guard_call(['retro-check', '--task', MAINLINE_TASK])
    guard_call(['check-reply', '--task', MAINLINE_TASK, '--has-artifact'])
    print(json.dumps(dashboard, ensure_ascii=False))


if __name__ == '__main__':
    main()
