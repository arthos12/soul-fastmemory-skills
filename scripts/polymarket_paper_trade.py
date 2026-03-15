#!/usr/bin/env python3
"""Create a paper-trading ledger from prediction JSONL.

Expected input fields per line:
- marketId / id
- question
- p_yes_me
- p_yes_mkt
- endDate (optional)
- url (optional)

Rules:
- If p_yes_me - p_yes_mkt > threshold => buy YES
- If p_yes_me - p_yes_mkt < -threshold => buy NO
- stake sizing: fixed or Kelly-lite
- outputs unresolved paper orders (no settlement yet)
"""
import argparse, json, os, statistics


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def kelly_fraction(prob, price):
    if price <= 0 or price >= 1:
        return 0.0
    b = (1 - price) / price
    q = 1 - prob
    f = (b * prob - q) / b
    return max(0.0, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--threshold', type=float, default=0.05)
    ap.add_argument('--sizing', choices=['fixed','kelly'], default='kelly')
    ap.add_argument('--fixed-stake', type=float, default=1000.0)
    ap.add_argument('--bankroll', type=float, default=100000.0)
    ap.add_argument('--kelly-scale', type=float, default=0.25)
    args = ap.parse_args()

    bankroll = args.bankroll
    orders = []
    with open(args.inp, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            p = float(r['p_yes_me'])
            m = float(r['p_yes_mkt'])
            edge = p - m
            side = None
            price = None
            est_prob = None
            if edge > args.threshold:
                side = 'YES'; price = m; est_prob = p
            elif edge < -args.threshold:
                side = 'NO'; price = 1 - m; est_prob = 1 - p
            else:
                continue

            if args.sizing == 'fixed':
                stake = args.fixed_stake
            else:
                frac = clamp(kelly_fraction(est_prob, price) * args.kelly_scale, 0.0, 0.25)
                stake = bankroll * frac
            if stake <= 0:
                continue
            contracts = stake / price if price > 0 else 0.0
            order = {
                'marketId': r.get('marketId') or r.get('id'),
                'question': r.get('question'),
                'url': r.get('url'),
                'endDate': r.get('endDate'),
                'side': side,
                'market_price_yes': round(m, 4),
                'fill_price': round(price, 4),
                'p_yes_me': round(p, 4),
                'edge': round(edge, 4),
                'stake': round(stake, 4),
                'contracts': round(contracts, 4),
                'status': 'OPEN',
            }
            orders.append(order)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        for o in orders:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')

    summary = {
        'input': args.inp,
        'output': args.out,
        'n_orders': len(orders),
        'total_stake': round(sum(o['stake'] for o in orders), 4) if orders else 0.0,
        'avg_edge': round(statistics.mean(o['edge'] for o in orders), 4) if orders else None,
        'bankroll_reference': args.bankroll,
        'threshold': args.threshold,
        'sizing': args.sizing,
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
