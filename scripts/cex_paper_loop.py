#!/usr/bin/env python3
import argparse, json, math, os, time
from datetime import datetime, timezone


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def ema(vals, n):
    if not vals:
        return []
    k = 2 / (n + 1)
    out = [vals[0]]
    for x in vals[1:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def read_klines(path):
    data = load_json(path, default=[])
    rows = []
    for r in data:
        try:
            rows.append({
                'ts': int(r['open_time']),
                'open': float(r['open']),
                'high': float(r['high']),
                'low': float(r['low']),
                'close': float(r['close']),
                'volume': float(r.get('volume', 0)),
            })
        except Exception:
            continue
    return rows


def infer_breakout_signals(rows, hold_bars=1, fee_bps=10, slippage_bps=5, strategy_id='cex_breakout', breakout_lookback=5, breakout_vol_mult=1.2, require_trend_filter=True):
    if len(rows) < 30:
        return [], {'reason': 'not_enough_rows'}
    closes = [r['close'] for r in rows]
    vols = [r['volume'] for r in rows]
    ema_fast = ema(closes, 5)
    ema_slow = ema(closes, 20)
    out = []
    reasons = {'selected': 0, 'filtered': 0}
    cost_rate = (fee_bps * 2 + slippage_bps * 2) / 10000.0

    for i in range(20, len(rows) - hold_bars):
        r = rows[i]
        lb = breakout_lookback
        prev_high = max(x['high'] for x in rows[i-lb:i])
        vol_avg = sum(vols[i-lb:i]) / lb
        trend_ok = (ema_fast[i] > ema_slow[i]) if require_trend_filter else True
        long_signal = closes[i] > prev_high and vols[i] > vol_avg * breakout_vol_mult and trend_ok
        if not long_signal:
            reasons['filtered'] += 1
            continue

        entry = closes[i]
        exitp = rows[i + hold_bars]['close']
        gross_ret = (exitp - entry) / entry
        net_ret = gross_ret - cost_rate
        prediction_prob = 0.58 if gross_ret > 0 else 0.52
        out.append({
            'ts': r['ts'],
            'venue': 'binance',
            'symbol': 'BTCUSDT',
            'timeframe': '5m',
            'side': 'LONG',
            'entryPrice': entry,
            'exitPrice': exitp,
            'gross_ret': gross_ret,
            'net_ret': net_ret,
            'fee_bps': fee_bps,
            'slippage_bps': slippage_bps,
            'prediction_prob': prediction_prob,
            'winFlag': net_ret > 0,
            'kind': 'realized',
            'strategy': strategy_id,
            'strategy_version': strategy_id,
            'reason_tag': 'breakout_volume_trend',
        })
        reasons['selected'] += 1
    return out, reasons


def infer_reversion_signals(rows, hold_bars=1, fee_bps=10, slippage_bps=5, strategy_id='cex_reversion', reversion_drop_threshold=-0.004):
    if len(rows) < 30:
        return [], {'reason': 'not_enough_rows'}
    closes = [r['close'] for r in rows]
    reasons = {'selected': 0, 'filtered': 0}
    cost_rate = (fee_bps * 2 + slippage_bps * 2) / 10000.0
    out = []
    for i in range(5, len(rows) - hold_bars):
        drop = (closes[i] - closes[i-3]) / closes[i-3]
        long_signal = drop < reversion_drop_threshold
        if not long_signal:
            reasons['filtered'] += 1
            continue
        entry = closes[i]
        exitp = rows[i + hold_bars]['close']
        gross_ret = (exitp - entry) / entry
        net_ret = gross_ret - cost_rate
        prediction_prob = 0.55 if gross_ret > 0 else 0.51
        out.append({
            'ts': rows[i]['ts'],
            'venue': 'binance',
            'symbol': 'BTCUSDT',
            'timeframe': '5m',
            'side': 'LONG',
            'entryPrice': entry,
            'exitPrice': exitp,
            'gross_ret': gross_ret,
            'net_ret': net_ret,
            'fee_bps': fee_bps,
            'slippage_bps': slippage_bps,
            'prediction_prob': prediction_prob,
            'winFlag': net_ret > 0,
            'kind': 'realized',
            'strategy': strategy_id,
            'strategy_version': strategy_id,
            'reason_tag': 'reversion_drop_buy',
        })
        reasons['selected'] += 1
    return out, reasons


def summarize(rows):
    n = len(rows)
    wins = sum(1 for r in rows if r.get('winFlag'))
    net = [r['net_ret'] for r in rows if isinstance(r.get('net_ret'), (int, float))]
    gross = [r['gross_ret'] for r in rows if isinstance(r.get('gross_ret'), (int, float))]
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for x in net:
        equity += x
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return {
        'n': n,
        'wins': wins,
        'winrate': (wins / n) if n else None,
        'gross_avg': (sum(gross) / len(gross)) if gross else None,
        'net_avg': (sum(net) / len(net)) if net else None,
        'net_sum': sum(net) if net else None,
        'max_drawdown_proxy': max_dd,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--strategy', required=True)
    ap.add_argument('--klines', default='data/cex/binance_btcusdt_5m.json')
    ap.add_argument('--outdir', default='data/cex')
    ap.add_argument('--tag', required=True)
    args = ap.parse_args()

    strat = load_json(args.strategy, default={}) or {}
    rows = read_klines(args.klines)
    mode = strat.get('mode', 'breakout')
    if mode == 'reversion':
        trades, reasons = infer_reversion_signals(
            rows,
            hold_bars=int(strat.get('holdBars', 1)),
            fee_bps=int(strat.get('feeBps', 10)),
            slippage_bps=int(strat.get('slippageBps', 5)),
            strategy_id=strat.get('name', args.tag),
            reversion_drop_threshold=float(strat.get('reversionDropThreshold', -0.004)),
        )
    else:
        trades, reasons = infer_breakout_signals(
            rows,
            hold_bars=int(strat.get('holdBars', 1)),
            fee_bps=int(strat.get('feeBps', 10)),
            slippage_bps=int(strat.get('slippageBps', 5)),
            strategy_id=strat.get('name', args.tag),
            breakout_lookback=int(strat.get('breakoutLookback', 5)),
            breakout_vol_mult=float(strat.get('breakoutVolMult', 1.2)),
            require_trend_filter=bool(strat.get('requireTrendFilter', True)),
        )

    day = datetime.now(timezone.utc).date().isoformat()
    orders_path = os.path.join(args.outdir, f'paper_orders_{day}_{args.tag}.jsonl')
    results_path = os.path.join(args.outdir, f'paper_results_{day}_{args.tag}.jsonl')
    append_jsonl(orders_path, trades)
    append_jsonl(results_path, trades)
    report = {
        'ts': int(time.time()),
        'tag': args.tag,
        'strategy': strat.get('name', args.tag),
        'trades_generated': len(trades),
        'selection_reasons': reasons,
        'summary': summarize(trades),
    }
    report_path = os.path.join(args.outdir, 'reports', f"hourly_report_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H')}_{args.tag}.json")
    dump_json(report_path, report)
    print(json.dumps({'orders': orders_path, 'results': results_path, 'report': report_path, **report}, ensure_ascii=False))


if __name__ == '__main__':
    main()
