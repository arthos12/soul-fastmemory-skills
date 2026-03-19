#!/usr/bin/env python3
"""Quick cross-exchange price spread check (no keys)."""
import json, time, urllib.request

EXCHANGES = {
    "binance": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
    "okx": "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT",
    "bybit": "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT",
}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"arb-check"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

def price_binance(d):
    return float(d["price"])

def price_okx(d):
    return float(d["data"][0]["last"])

def price_bybit(d):
    return float(d["result"]["list"][0]["lastPrice"])

PARSERS = {"binance": price_binance, "okx": price_okx, "bybit": price_bybit}

prices = {}
for name, url in EXCHANGES.items():
    try:
        data = fetch(url)
        prices[name] = PARSERS[name](data)
    except Exception:
        prices[name] = None

valid = {k:v for k,v in prices.items() if isinstance(v,(int,float))}
if len(valid) >= 2:
    high = max(valid.items(), key=lambda x: x[1])
    low = min(valid.items(), key=lambda x: x[1])
    spread = (high[1]-low[1]) / low[1]
else:
    high = low = (None, None)
    spread = None

out = {
    "ts": int(time.time()),
    "prices": prices,
    "high": high,
    "low": low,
    "spread_pct": round(spread*100, 4) if spread is not None else None,
}
print(json.dumps(out, ensure_ascii=False))
