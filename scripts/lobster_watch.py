#!/usr/bin/env python3
"""Lobster watch: fetch token data from DexScreener and write snapshot.

Token:
  0xeccbb861c0dda7efd964010085488b69317e4444

Outputs:
- data/lobster/lobster_snapshots.jsonl (append)
- data/lobster/lobster_latest.json

Usage:
  python3 scripts/lobster_watch.py
"""

import json, os, time, datetime
from urllib.request import urlopen, Request

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
TOKEN="0xeccbb861c0dda7efd964010085488b69317e4444"
URL=f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN}"
OUT_DIR=os.path.join(ROOT,'data','lobster')
JSONL=os.path.join(OUT_DIR,'lobster_snapshots.jsonl')
LATEST=os.path.join(OUT_DIR,'lobster_latest.json')


def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def fetch():
    req=Request(URL, headers={"User-Agent":"openclaw-lobster-watch/1.0"})
    with urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw=fetch()
    pairs=raw.get('pairs') or []
    # choose best pair by liquidity.usd (fallback volume)
    def key(p):
        liq=(p.get('liquidity') or {}).get('usd') or 0
        vol=(p.get('volume') or {}).get('h24') or 0
        return (float(liq or 0), float(vol or 0))
    best=max(pairs, key=key) if pairs else {}

    snap={
        'ts': now(),
        'token': TOKEN,
        'pairAddress': best.get('pairAddress'),
        'dexId': best.get('dexId'),
        'chainId': best.get('chainId'),
        'url': best.get('url'),
        'priceUsd': best.get('priceUsd'),
        'liquidityUsd': (best.get('liquidity') or {}).get('usd'),
        'fdv': best.get('fdv'),
        'mcap': best.get('marketCap'),
        'volume24h': (best.get('volume') or {}).get('h24'),
        'txns24h': (best.get('txns') or {}).get('h24'),
        'priceChange24h': (best.get('priceChange') or {}).get('h24'),
        'priceChange6h': (best.get('priceChange') or {}).get('h6'),
        'priceChange1h': (best.get('priceChange') or {}).get('h1'),
        'pairLabel': f"{(best.get('baseToken') or {}).get('symbol','')} / {(best.get('quoteToken') or {}).get('symbol','')}".strip(),
    }

    with open(JSONL,'a',encoding='utf-8') as f:
        f.write(json.dumps(snap, ensure_ascii=False)+'\n')
    with open(LATEST,'w',encoding='utf-8') as f:
        json.dump({'snapshot': snap, 'raw': raw}, f, ensure_ascii=False, indent=2)

    # Human one-line summary
    print(
        f"LOBSTER priceUsd={snap['priceUsd']} liqUsd={snap['liquidityUsd']} vol24h={snap['volume24h']} "
        f"chg24h={snap['priceChange24h']}% pair={snap['pairLabel']}"
    )

if __name__=='__main__':
    main()
