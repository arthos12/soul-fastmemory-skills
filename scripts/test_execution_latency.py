#!/usr/bin/env python3
import argparse, json, os, statistics, time
from urllib.parse import urlencode

import requests

UA = {"User-Agent": "openclaw/execution-latency-test"}
GAMMA = "https://gamma-api.polymarket.com/markets"
BINANCE_TICKER = "https://api.binance.com/api/v3/ticker/price"


def pct_change(a, b):
    if a in (None, 0) or b is None:
        return None
    return (b - a) / a


def bps(x):
    return None if x is None else x * 10000.0


def fetch_binance_price(symbol="BTCUSDT"):
    t0 = time.perf_counter()
    r = requests.get(BINANCE_TICKER, params={"symbol": symbol}, headers=UA, timeout=10)
    r.raise_for_status()
    data = r.json()
    t1 = time.perf_counter()
    return {
        "symbol": symbol,
        "price": float(data["price"]),
        "latency_ms": round((t1 - t0) * 1000, 2),
        "ts": time.time(),
    }


def fetch_pm_market(mid):
    t0 = time.perf_counter()
    r = requests.get(GAMMA, params={"id": mid}, headers=UA, timeout=20)
    r.raise_for_status()
    arr = r.json()
    t1 = time.perf_counter()
    if not arr:
        raise RuntimeError(f"PM market not found: {mid}")
    m = arr[0]
    prices = m.get("outcomePrices")
    if isinstance(prices, str):
        prices = json.loads(prices)
    prices = [float(x) for x in prices]
    return {
        "marketId": str(mid),
        "question": m.get("question"),
        "prices": prices,
        "best_price": max(prices) if prices else None,
        "latency_ms": round((t1 - t0) * 1000, 2),
        "ts": time.time(),
    }


def summarize_num(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    if not xs:
        return None
    return {
        "n": len(xs),
        "min": min(xs),
        "max": max(xs),
        "avg": round(sum(xs) / len(xs), 4),
        "median": round(statistics.median(xs), 4),
        "p95": round(sorted(xs)[max(0, min(len(xs)-1, int(len(xs)*0.95)-1))], 4) if xs else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venue", choices=["binance", "pm"], required=True)
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--pm-market-id")
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--decision-delay-ms", type=int, default=1500)
    ap.add_argument("--submit-delay-ms", type=int, default=1500)
    ap.add_argument("--safe-drift-bps", type=float, default=10.0)
    ap.add_argument("--out", default="data/execution_latency/latest.json")
    args = ap.parse_args()

    samples = []
    for i in range(args.rounds):
        if args.venue == "binance":
            snap1 = fetch_binance_price(args.symbol)
        else:
            if not args.pm_market_id:
                raise SystemExit("--pm-market-id required for venue=pm")
            snap1 = fetch_pm_market(args.pm_market_id)

        time.sleep(args.decision_delay_ms / 1000.0)

        if args.venue == "binance":
            snap2 = fetch_binance_price(args.symbol)
            p1, p2 = snap1["price"], snap2["price"]
        else:
            snap2 = fetch_pm_market(args.pm_market_id)
            p1, p2 = snap1["best_price"], snap2["best_price"]

        time.sleep(args.submit_delay_ms / 1000.0)

        if args.venue == "binance":
            snap3 = fetch_binance_price(args.symbol)
            p3 = snap3["price"]
        else:
            snap3 = fetch_pm_market(args.pm_market_id)
            p3 = snap3["best_price"]

        total_ms = round((snap3["ts"] - snap1["ts"]) * 1000, 2)
        drift_1_2 = pct_change(p1, p2)
        drift_1_3 = pct_change(p1, p3)
        sample = {
            "round": i + 1,
            "signal_price": p1,
            "confirm_price": p2,
            "submit_price": p3,
            "fetch1_latency_ms": snap1["latency_ms"],
            "fetch2_latency_ms": snap2["latency_ms"],
            "fetch3_latency_ms": snap3["latency_ms"],
            "decision_delay_ms": args.decision_delay_ms,
            "submit_delay_ms": args.submit_delay_ms,
            "end_to_end_ms": total_ms,
            "drift_signal_to_confirm_bps": round(bps(drift_1_2), 4) if drift_1_2 is not None else None,
            "drift_signal_to_submit_bps": round(bps(drift_1_3), 4) if drift_1_3 is not None else None,
            "safe": (abs(bps(drift_1_3)) <= args.safe_drift_bps) if drift_1_3 is not None else None,
        }
        samples.append(sample)

    summary = {
        "venue": args.venue,
        "symbol": args.symbol if args.venue == "binance" else None,
        "pm_market_id": args.pm_market_id if args.venue == "pm" else None,
        "rounds": args.rounds,
        "decision_delay_ms": args.decision_delay_ms,
        "submit_delay_ms": args.submit_delay_ms,
        "safe_drift_bps": args.safe_drift_bps,
        "fetch1_latency_ms": summarize_num([s["fetch1_latency_ms"] for s in samples]),
        "fetch2_latency_ms": summarize_num([s["fetch2_latency_ms"] for s in samples]),
        "fetch3_latency_ms": summarize_num([s["fetch3_latency_ms"] for s in samples]),
        "end_to_end_ms": summarize_num([s["end_to_end_ms"] for s in samples]),
        "drift_signal_to_confirm_bps": summarize_num([s["drift_signal_to_confirm_bps"] for s in samples]),
        "drift_signal_to_submit_bps": summarize_num([s["drift_signal_to_submit_bps"] for s in samples]),
        "safe_rate": round(sum(1 for s in samples if s.get("safe")) / len(samples), 4) if samples else None,
    }

    out = {"summary": summary, "samples": samples, "ts": int(time.time())}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
