#!/usr/bin/env python3
"""PM Paper Loop (local-first)

Goal: run paper trading loop with minimal LLM usage.
- Pull a small slice of markets from Gamma API (cached)
- Generate paper orders per strategy params
- Backfill results for resolved/closed markets
- Emit hourly report JSON

Usage:
  python3 scripts/pm_paper_loop.py --strategy strategies/br_v2_highprob.json \
    --outdir data/polymarket --tag br_v2

Notes:
- This script is intentionally conservative on API calls.
"""

import argparse, datetime as dt, json, os, time
from urllib.parse import urlencode

DEDUP_LOOKBACK_HOURS = 24

import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
UA = {"User-Agent": "openclaw/pm-paper-loop"}


def utcnow():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def norm_list(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return None
    return x


def fetch_markets_slice(limit=200, offset=0, active=True, closed=False):
    params = {
        "limit": limit,
        "offset": offset,
        "active": "true" if active else "false",
        "closed": "true" if closed else "false",
    }
    r = requests.get(GAMMA, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    return r.json()


def load_or_refresh_cache(cache_path, max_age_sec, limit, offset, active, closed):
    meta_path = cache_path + ".meta.json"
    meta = load_json(meta_path, default=None) or {}
    now = int(time.time())
    if os.path.exists(cache_path) and meta.get("ts") and now - meta["ts"] <= max_age_sec:
        return load_json(cache_path, default=[])
    data = fetch_markets_slice(limit=limit, offset=offset, active=active, closed=closed)
    dump_json(cache_path, data)
    dump_json(meta_path, {"ts": now, "limit": limit, "offset": offset, "active": active, "closed": closed})
    return data


def parse_end_minutes(m):
    try:
        end = dt.datetime.fromisoformat((m.get("endDate") or "").replace("Z", "+00:00"))
        mins = (end - utcnow()).total_seconds() / 60
        return mins
    except Exception:
        return None


def pick_highprob(outcomes, prices, min_price):
    # pick max price side
    idx = max(range(len(prices)), key=lambda i: prices[i])
    p = prices[idx]
    o = outcomes[idx]
    if min_price <= p < 1.0:
        return o, p
    return None


def load_recent_market_ids(outdir, lookback_hours=DEDUP_LOOKBACK_HOURS):
    recent = set()
    cutoff = time.time() - lookback_hours * 3600
    if not os.path.isdir(outdir):
        return recent
    for name in os.listdir(outdir):
        if not name.startswith('paper_orders_') or not name.endswith('.jsonl'):
            continue
        path = os.path.join(outdir, name)
        try:
            if os.path.getmtime(path) < cutoff:
                continue
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                        mid = row.get('marketId')
                        if mid is not None:
                            recent.add(str(mid))
                    except Exception:
                        continue
        except Exception:
            continue
    return recent


def generate_orders(markets, strat, tag, outdir):
    orders = []
    now_ts = int(time.time())
    recent_market_ids = load_recent_market_ids(outdir, lookback_hours=int(strat.get('dedupLookbackHours', DEDUP_LOOKBACK_HOURS)))

    for m in markets:
        if m.get("closed") is True:
            continue
        if str(m.get("id")) in recent_market_ids:
            continue
        if strat.get("requireAcceptingOrders", True) and m.get("acceptingOrders") is False:
            continue

        mins = parse_end_minutes(m)
        if mins is None:
            continue
        if mins <= 0:
            continue
        if mins > strat.get("maxMinsToEnd", 24 * 60):
            continue

        q = (m.get("question") or "")
        ql = q.lower()
        if strat.get("keywords"):
            if not any(k.lower() in ql for k in strat["keywords"]):
                continue

        outcomes = norm_list(m.get("outcomes"))
        prices = norm_list(m.get("outcomePrices"))
        if not isinstance(outcomes, list) or not isinstance(prices, list) or len(outcomes) != len(prices):
            continue
        try:
            prices = [float(p) for p in prices]
        except Exception:
            continue

        picked = None
        if strat.get("mode") == "highprob":
            picked = pick_highprob(outcomes, prices, strat.get("minPrice", 0.9))

        if not picked:
            continue

        outcome, price = picked
        # avoid 0 price orders
        if price <= 0:
            continue
        # enforce floor tick
        min_tick = float(m.get("orderPriceMinTickSize") or strat.get("minTick", 0.0005))
        if price < min_tick:
            continue

        orders.append(
            {
                "ts": now_ts,
                "marketId": m.get("id"),
                "slug": m.get("slug"),
                "title": q,
                "minsToEnd": mins,
                "outcome": outcome,
                "limitPrice": round(price, 6),
                "sizeUSD": strat.get("sizeUSD", 50),
                "type": "paper",
                "strategy": strat.get("name", "pm-paper"),
                "reason": f"{strat.get('mode')}>= {strat.get('minPrice')}",
                "source": strat.get("source", "gamma-api"),
                "tag": tag,
            }
        )

        if len(orders) >= strat.get("maxOrders", 30):
            break

    return orders


def fetch_market_by_id(mid):
    r = requests.get(GAMMA, params={"id": mid}, headers=UA, timeout=30)
    r.raise_for_status()
    arr = r.json()
    return arr[0] if arr else None


def backfill_results(orders, tag):
    """Backfill both realized (resolved) and mark-to-market (unresolved) results.

    - If umaResolutionStatus==resolved and final outcomePrices are 0/1: treat as realized.
    - Otherwise: compute mark-to-market PnL using current outcomePrices.

    This enables fast iteration without waiting UMA resolution.
    """
    results = []
    ts = int(time.time())
    for o in orders:
        mid = o.get("marketId")
        m = fetch_market_by_id(mid)
        if not m:
            continue
        outcomes = norm_list(m.get("outcomes"))
        prices = norm_list(m.get("outcomePrices"))
        status = m.get("umaResolutionStatus")
        if not isinstance(outcomes, list) or not isinstance(prices, list) or len(outcomes) != len(prices):
            continue
        try:
            prices_f = [float(p) for p in prices]
        except Exception:
            continue

        picked = o.get("outcome")
        lp = float(o.get("limitPrice") or 0)
        size = float(o.get("sizeUSD") or 0)
        if lp <= 0 or size <= 0:
            continue
        shares = size / lp

        # mark-to-market using current picked price
        cur_price = None
        for oc, p in zip(outcomes, prices_f):
            if oc == picked:
                cur_price = p
                break

        # realized if market is closed/resolved and there is a winner side by terminal price
        win = None
        is_terminal = (status == "resolved") or (m.get("closed") is True)
        if is_terminal:
            for oc, p in zip(outcomes, prices_f):
                if p >= 0.999:
                    win = oc
                    break
            if win is None and len(prices_f) == 2:
                # fallback: treat near-binary terminal prices as final even if not exact 1.0/0.0
                max_idx = max(range(len(prices_f)), key=lambda i: prices_f[i])
                max_p = prices_f[max_idx]
                min_p = min(prices_f)
                if max_p >= 0.9 and min_p <= 0.1:
                    win = outcomes[max_idx]

        if win is not None:
            win_flag = picked == win
            payout = shares if win_flag else 0.0
            pnl = payout - size
            roi = pnl / size if size else None
            kind = "realized"
        else:
            # unrealized / mark-to-market
            if cur_price is None:
                continue
            m2m = shares * cur_price
            pnl = m2m - size
            roi = pnl / size if size else None
            win_flag = None
            kind = "m2m"

        results.append(
            {
                "ts_checked": ts,
                "kind": kind,
                "marketId": mid,
                "slug": o.get("slug"),
                "title": o.get("title"),
                "picked": picked,
                "win": win,
                "winFlag": win_flag,
                "limitPrice": lp,
                "curPrice": cur_price,
                "sizeUSD": size,
                "shares_est": shares,
                "pnl_est": pnl,
                "roi_est": roi,
                "umaResolutionStatus": status,
                "closed": m.get("closed"),
                "endDate": m.get("endDate"),
                "strategy": o.get("strategy"),
                "tag": tag,
            }
        )
    return results


def summarize(results):
    n = len(results)
    realized = [r for r in results if r.get("kind") == "realized"]
    m2m = [r for r in results if r.get("kind") == "m2m"]

    def s(rows):
        n2 = len(rows)
        wins = sum(1 for r in rows if r.get("winFlag") is True)
        rois = [r["roi_est"] for r in rows if isinstance(r.get("roi_est"), (int, float))]
        pnls = [r["pnl_est"] for r in rows if isinstance(r.get("pnl_est"), (int, float))]
        return {
            "n": n2,
            "wins": wins,
            "winrate": (wins / n2) if n2 else None,
            "roi_avg": (sum(rois) / len(rois)) if rois else None,
            "pnl_sum": sum(pnls) if pnls else None,
            "roi_n": len(rois),
        }

    out = {"n": n, "realized": s(realized), "m2m": s(m2m)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True, help="Path to strategy json")
    ap.add_argument("--outdir", default="data/polymarket")
    ap.add_argument("--tag", default="run")
    ap.add_argument("--cache-age-sec", type=int, default=300)
    ap.add_argument("--scan-pages", type=int, default=10)
    ap.add_argument("--page-size", type=int, default=200)
    args = ap.parse_args()

    strat = load_json(args.strategy, default={})
    run_tag = args.tag

    # cache: pull a few pages
    markets = []
    for i in range(args.scan_pages):
        offset = i * args.page_size
        cache_path = os.path.join(args.outdir, "cache", f"gamma_active_{offset}_{args.page_size}.json")
        markets.extend(
            load_or_refresh_cache(
                cache_path,
                max_age_sec=args.cache_age_sec,
                limit=args.page_size,
                offset=offset,
                active=True,
                closed=False,
            )
        )

    orders = generate_orders(markets, strat, tag=run_tag, outdir=args.outdir)

    day = dt.datetime.utcnow().date().isoformat()
    orders_path = os.path.join(args.outdir, f"paper_orders_{day}_{run_tag}.jsonl")
    append_jsonl(orders_path, orders)

    # backfill resolved results for generated orders (best-effort)
    results = backfill_results(orders, tag=run_tag)
    results_path = os.path.join(args.outdir, f"paper_results_{day}_{run_tag}.jsonl")
    append_jsonl(results_path, results)

    report = {
        "ts": int(time.time()),
        "tag": run_tag,
        "strategy": strat.get("name"),
        "orders_generated": len(orders),
        "results_backfilled": len(results),
        "summary": summarize(results),
    }
    hour = dt.datetime.utcnow().strftime("%Y-%m-%d_%H")
    report_path = os.path.join(args.outdir, "reports", f"hourly_report_{hour}_{run_tag}.json")
    dump_json(report_path, report)

    print(json.dumps({"orders": orders_path, "results": results_path, "report": report_path, **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
