#!/usr/bin/env python3
"""Pull Polymarket markets from Gamma API.

Outputs JSONL lines with: id, question, endDate, liquidity, volume, outcomes, outcomePrices.

Usage:
  python3 scripts/polymarket_pull.py --limit 50 --active 1 --closed 0 --out data/polymarket/markets_YYYY-MM-DD.jsonl
"""

import argparse, datetime, json, os, sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://gamma-api.polymarket.com/markets"


def fetch(params: dict):
    url = BASE + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "openclaw/pm-pull"})
    with urlopen(req, timeout=20) as r:
        data = r.read()
    return json.loads(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--active", type=int, default=1)
    ap.add_argument("--closed", type=int, default=0)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    params = {
        "limit": args.limit,
        "active": "true" if args.active else "false",
        "closed": "true" if args.closed else "false",
    }
    markets = fetch(params)

    out_path = args.out
    if not out_path:
        today = datetime.date.today().isoformat()
        out_path = f"data/polymarket/markets_{today}.jsonl"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for m in markets:
            # outcomes/outcomePrices are JSON-in-string in this API
            try:
                outcomes = json.loads(m.get("outcomes") or "[]")
            except Exception:
                outcomes = m.get("outcomes")
            try:
                prices = json.loads(m.get("outcomePrices") or "[]")
            except Exception:
                prices = m.get("outcomePrices")

            rec = {
                "pulledAt": datetime.datetime.utcnow().isoformat() + "Z",
                "id": m.get("id"),
                "question": m.get("question"),
                "slug": m.get("slug"),
                "endDate": m.get("endDate"),
                "active": m.get("active"),
                "closed": m.get("closed"),
                "liquidity": m.get("liquidity"),
                "volume": m.get("volume"),
                "outcomes": outcomes,
                "outcomePrices": prices,
                "url": f"https://polymarket.com/market/{m.get('slug')}" if m.get("slug") else None,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(out_path)


if __name__ == "__main__":
    main()
