#!/usr/bin/env python3
"""Diagnose BTC/ETH 5m markets: web list -> gamma market -> clob book."""
import json, os, subprocess, requests

WEB_URL = "https://polymarket.com/zh/crypto/5M"
GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK = "https://clob.polymarket.com/book"

# 1) fetch web markets
out = subprocess.check_output(["node", "/root/.openclaw/workspace/scripts/pm_web_markets_dump.js", WEB_URL]).decode("utf-8", errors="ignore")
obj = json.loads(out)
markets = obj.get("markets", [])

# 2) pick BTC/ETH 5m
candidates = [m for m in markets if ("5" in (m.get("question") or "") or "5m" in (m.get("question") or "")) and ("btc" in (m.get("question") or "").lower() or "bitcoin" in (m.get("question") or "").lower() or "eth" in (m.get("question") or "").lower() or "以太坊" in (m.get("question") or ""))]
# fallback: any BTC/ETH items
if not candidates:
    candidates = [m for m in markets if ("btc" in (m.get("question") or "").lower() or "bitcoin" in (m.get("question") or "").lower() or "eth" in (m.get("question") or "").lower() or "以太坊" in (m.get("question") or ""))]

print("web_candidates", len(candidates))

# 3) for each candidate, try gamma slug lookup
results = []
for m in candidates[:10]:
    slug = m.get("slug")
    r = requests.get(GAMMA, params={"slug": slug}, timeout=15)
    data = r.json()
    mk = data[0] if isinstance(data, list) and data else None
    if not mk:
        results.append({"slug": slug, "gamma": False})
        continue
    clob = mk.get("clobTokenIds")
    if isinstance(clob, str):
        try:
            clob = json.loads(clob)
        except Exception:
            clob = None
    tid = clob[0] if isinstance(clob, list) and clob else None
    book = None
    if tid:
        book = requests.get(CLOB_BOOK, params={"token_id": tid}, timeout=15).json()
    bids = (book or {}).get("bids") or []
    asks = (book or {}).get("asks") or []
    best_bid = bids[0]["price"] if bids else None
    best_ask = asks[0]["price"] if asks else None
    results.append({
        "slug": slug,
        "gamma": True,
        "token_id": tid,
        "best_bid": best_bid,
        "best_ask": best_ask,
    })

print(json.dumps(results, ensure_ascii=False, indent=2))
