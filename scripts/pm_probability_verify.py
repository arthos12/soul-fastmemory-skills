#!/usr/bin/env python3
import argparse, json, math, os
from collections import defaultdict


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


def bucket_label(p, width=0.05):
    lo = math.floor(float(p) / width) * width
    hi = lo + width
    return f"{lo:.2f}-{hi:.2f}"


def safe_num(x):
    try:
        return float(x)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--bucket-width', type=float, default=0.05)
    args = ap.parse_args()

    rows = read_jsonl(args.results)
    realized = [r for r in rows if r.get('kind') == 'realized' and isinstance(r.get('winFlag'), bool)]

    buckets = defaultdict(lambda: {'n': 0, 'wins': 0, 'pred_sum': 0.0, 'edge_sum': 0.0})
    brier_sum = 0.0
    edge_realized = []

    for r in realized:
        p = safe_num(r.get('prediction_prob'))
        edge = safe_num(r.get('edge'))
        y = 1.0 if r.get('winFlag') else 0.0
        if p is None:
            continue
        label = bucket_label(p, width=args.bucket_width)
        buckets[label]['n'] += 1
        buckets[label]['wins'] += int(y)
        buckets[label]['pred_sum'] += p
        if edge is not None:
            buckets[label]['edge_sum'] += edge
            edge_realized.append((edge, y))
        brier_sum += (p - y) ** 2

    bucket_rows = []
    ece_num = 0.0
    total_n = sum(v['n'] for v in buckets.values())
    for label in sorted(buckets.keys()):
        v = buckets[label]
        n = v['n']
        pred_avg = v['pred_sum'] / n if n else None
        hit_rate = v['wins'] / n if n else None
        edge_avg = v['edge_sum'] / n if n else None
        gap = abs(pred_avg - hit_rate) if pred_avg is not None and hit_rate is not None else None
        if gap is not None:
            ece_num += gap * n
        bucket_rows.append({
            'bucket': label,
            'n': n,
            'pred_avg': pred_avg,
            'hit_rate': hit_rate,
            'calibration_gap': gap,
            'edge_avg': edge_avg,
        })

    # coarse discrimination: compare high-vs-low prediction groups
    pred_sorted = sorted(
        [(safe_num(r.get('prediction_prob')), 1.0 if r.get('winFlag') else 0.0) for r in realized if safe_num(r.get('prediction_prob')) is not None],
        key=lambda x: x[0]
    )
    discrim = None
    if len(pred_sorted) >= 4:
        mid = len(pred_sorted) // 2
        low = pred_sorted[:mid]
        high = pred_sorted[mid:]
        low_hit = sum(y for _, y in low) / len(low)
        high_hit = sum(y for _, y in high) / len(high)
        discrim = {
            'low_half_hit_rate': low_hit,
            'high_half_hit_rate': high_hit,
            'gap': high_hit - low_hit,
        }

    out = {
        'results_path': args.results,
        'realized_n': len(realized),
        'bucket_width': args.bucket_width,
        'brier_score': (brier_sum / len(realized)) if realized else None,
        'ece': (ece_num / total_n) if total_n else None,
        'discrimination': discrim,
        'buckets': bucket_rows,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
