#!/usr/bin/env python3
"""Local prediction backtest simulator for binary event markets.

Input: JSONL with fields:
- id
- question
- p_true_me      (our predicted probability, 0..1)
- p_mkt_yes      (market yes price / implied prob, 0..1)
- outcome        (1=yes happened, 0=no happened)
Optional:
- confidence     (0..1), default 1.0
- notes

Strategy:
- If edge = p_true_me - p_mkt_yes > threshold => buy YES
- If edge < -threshold => buy NO
- stake via fixed or Kelly-fraction-lite
- Settle at 1 on correct side, 0 on wrong side

Outputs summary + optional ledger jsonl.
"""
import argparse, json, math, os, statistics


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def kelly_fraction(prob, price):
    # yes-side only; b = (1-price)/price in binary contract terms
    if price <= 0 or price >= 1:
        return 0.0
    b = (1 - price) / price
    q = 1 - prob
    f = (b * prob - q) / b
    return max(0.0, f)


def decide(rec, threshold, sizing, bankroll, fixed_stake, kelly_scale):
    p = float(rec['p_true_me'])
    m = float(rec['p_mkt_yes'])
    edge = p - m
    side = None
    price = None
    est_prob = None
    if edge > threshold:
        side = 'YES'
        price = m
        est_prob = p
    elif edge < -threshold:
        side = 'NO'
        price = 1 - m
        est_prob = 1 - p
    else:
        return None

    if sizing == 'fixed':
        stake = fixed_stake
    else:
        frac = kelly_fraction(est_prob, price) * kelly_scale
        frac = clamp(frac, 0.0, 0.25)
        stake = bankroll * frac
    if stake <= 0:
        return None
    return {
        'side': side,
        'price': price,
        'stake': round(stake, 4),
        'edge': round(edge, 4),
        'est_prob': round(est_prob, 4),
    }


def settle(side, price, stake, outcome):
    win = (side == 'YES' and outcome == 1) or (side == 'NO' and outcome == 0)
    contracts = stake / price if price > 0 else 0
    payout = contracts * (1.0 if win else 0.0)
    pnl = payout - stake
    roi = pnl / stake if stake else 0.0
    return win, payout, pnl, roi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--ledger-out', default='')
    ap.add_argument('--threshold', type=float, default=0.05)
    ap.add_argument('--sizing', choices=['fixed','kelly'], default='fixed')
    ap.add_argument('--fixed-stake', type=float, default=100.0)
    ap.add_argument('--bankroll', type=float, default=10000.0)
    ap.add_argument('--kelly-scale', type=float, default=0.25)
    args = ap.parse_args()

    bankroll = args.bankroll
    trades = []
    with open(args.inp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            d = decide(rec, args.threshold, args.sizing, bankroll, args.fixed_stake, args.kelly_scale)
            if not d:
                continue
            outcome = int(rec['outcome'])
            win, payout, pnl, roi = settle(d['side'], d['price'], d['stake'], outcome)
            bankroll += pnl
            trade = {
                'id': rec.get('id'),
                'question': rec.get('question'),
                'side': d['side'],
                'price': d['price'],
                'stake': d['stake'],
                'edge': d['edge'],
                'est_prob': d['est_prob'],
                'outcome': outcome,
                'win': win,
                'pnl': round(pnl, 4),
                'roi': round(roi, 4),
                'bankroll_after': round(bankroll, 4),
            }
            trades.append(trade)

    if args.ledger_out:
        os.makedirs(os.path.dirname(args.ledger_out), exist_ok=True)
        with open(args.ledger_out, 'w', encoding='utf-8') as f:
            for t in trades:
                f.write(json.dumps(t, ensure_ascii=False) + '\n')

    pnls = [t['pnl'] for t in trades]
    wins = [t['win'] for t in trades]
    summary = {
        'input': args.inp,
        'n_trades': len(trades),
        'win_rate': round(sum(wins)/len(wins), 4) if wins else None,
        'total_pnl': round(sum(pnls), 4) if pnls else 0.0,
        'avg_pnl': round(statistics.mean(pnls), 4) if pnls else None,
        'median_pnl': round(statistics.median(pnls), 4) if pnls else None,
        'final_bankroll': round(bankroll, 4),
        'threshold': args.threshold,
        'sizing': args.sizing,
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
