#!/usr/bin/env python3
"""Score prediction batches.

This is *not* a resolution score (no outcomes yet). It measures calibration-vs-market proxy:
- abs diff to market probability
- mean abs diff

Usage:
  python3 scripts/polymarket_score.py data/polymarket/predictions_*.jsonl
"""

import json, sys, statistics


def main(path: str):
    diffs = []
    n = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            r = json.loads(line)
            p = float(r['p_yes_me'])
            m = float(r['p_yes_mkt'])
            diffs.append(abs(p-m))
            n += 1
    mean = statistics.mean(diffs) if diffs else None
    p50 = statistics.median(diffs) if diffs else None
    mx = max(diffs) if diffs else None
    print(json.dumps({"file": path, "n": n, "mean_abs_diff_to_mkt": mean, "median_abs_diff_to_mkt": p50, "max_abs_diff_to_mkt": mx}, ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('need path', file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
