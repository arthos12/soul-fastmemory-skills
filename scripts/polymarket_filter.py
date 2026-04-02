#!/usr/bin/env python3
"""Filter Polymarket markets for training.

Goal (brain upgrade): stop wasting training on low-signal / non-forecastable / joke markets.

Heuristics:
- Keep only Yes/No markets
- Exclude nonsense/joke keywords
- Prefer higher liquidity/volume

Usage:
  python3 scripts/polymarket_filter.py --in markets.jsonl --out markets_filtered.jsonl --limit 30
"""

import argparse, json, re

EXCLUDE_PATTERNS = [
    r"jesus",
    r"christ return",
    r"aliens",
    r"rapture",
    r"ufo",
    r"frankenstein",
]


def parse_num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='outp', required=True)
    ap.add_argument('--limit', type=int, default=30)
    args = ap.parse_args()

    rx = re.compile('|'.join(EXCLUDE_PATTERNS), re.I)

    rows = []
    with open(args.inp, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            m = json.loads(line)
            outcomes = m.get('outcomes') or []
            if outcomes != ['Yes','No']:
                continue
            q = (m.get('question') or '')
            if rx.search(q):
                continue
            # score by liquidity + volume (log-ish)
            liq = parse_num(m.get('liquidity'))
            vol = parse_num(m.get('volume'))
            score = liq + 0.05 * vol
            rows.append((score, m))

    rows.sort(key=lambda t: t[0], reverse=True)
    picked = [m for _, m in rows[:args.limit]]

    with open(args.outp, 'w', encoding='utf-8') as f:
        for m in picked:
            f.write(json.dumps(m, ensure_ascii=False) + '\n')

    print(json.dumps({"in": args.inp, "out": args.outp, "picked": len(picked), "candidates": len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
