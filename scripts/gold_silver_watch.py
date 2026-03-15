#!/usr/bin/env python3
"""Gold/Silver watch using Stooq daily CSV (no API key).

Fetches XAUUSD and XAGUSD (daily close) and writes snapshot.

Outputs:
- data/metals/metals_snapshots.jsonl (append)
- data/metals/metals_latest.json

Usage:
  python3 scripts/gold_silver_watch.py
"""

import json, os, datetime
from urllib.request import urlopen, Request

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT_DIR=os.path.join(ROOT,'data','metals')
JSONL=os.path.join(OUT_DIR,'metals_snapshots.jsonl')
LATEST=os.path.join(OUT_DIR,'metals_latest.json')

SYMS={'xauusd':'GOLD','xagusd':'SILVER'}

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def fetch_sym(sym:str):
    url=f'https://stooq.com/q/l/?s={sym}&i=d'
    req=Request(url, headers={'User-Agent':'openclaw-metals-watch/1.0'})
    txt=urlopen(req, timeout=20).read().decode('utf-8').strip()
    # Stooq sometimes returns single CSV line without header:
    # SYMBOL,YYYYMMDD,HHMMSS,OPEN,HIGH,LOW,CLOSE,VOLUME,
    line=txt.splitlines()[-1] if txt else ''
    parts=[p.strip() for p in line.split(',')]
    close=parts[6] if len(parts)>6 else None
    date=parts[1] if len(parts)>1 else None
    return {'sym': sym, 'date': date, 'close': close, 'raw': line}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data={k:fetch_sym(k) for k in SYMS}
    snap={'ts': now(), 'source':'stooq', 'symbols': data}
    with open(JSONL,'a',encoding='utf-8') as f:
        f.write(json.dumps(snap,ensure_ascii=False)+'\n')
    with open(LATEST,'w',encoding='utf-8') as f:
        json.dump(snap,f,ensure_ascii=False,indent=2)

    g=data['xauusd']['close']
    s=data['xagusd']['close']
    print(f"METALS gold_close={g} silver_close={s} date={data['xauusd']['date']}")

if __name__=='__main__':
    main()
