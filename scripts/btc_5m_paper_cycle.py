#!/usr/bin/env python3
import os, json, datetime, urllib.request, statistics
URL='https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=30'

def get_json(url):
    req=urllib.request.Request(url, headers={'User-Agent':'openclaw/btc5m-paper'})
    with urllib.request.urlopen(req, timeout=20) as r: return json.loads(r.read().decode())

def main():
    rows=get_json(URL)
    closes=[float(r[4]) for r in rows]
    cur=closes[-1]; prev5=closes[-6]
    ret5=(cur-prev5)/prev5
    vol5=statistics.pstdev(closes[-6:])/cur if len(closes)>=6 else 0
    mode='trend' if vol5 < 0.0015 else 'meanrev'
    direction=('up' if ret5>0 else 'down') if mode=='trend' else ('down' if ret5>0 else 'up')
    prob=0.53 if mode=='trend' else 0.52
    now=datetime.datetime.utcnow().replace(microsecond=0)
    due=(now + datetime.timedelta(minutes=5)).isoformat()+'Z'
    rec={'createdAt': now.isoformat()+'Z','symbol':'BTCUSDT','window':'5m','mode':mode,'direction':direction,'prob':prob,'referencePrice':cur,'ret5':round(ret5,6),'vol5':round(vol5,6),'status':'OPEN','resultCheckDueAt':due}
    os.makedirs('data/btc5m_paper', exist_ok=True)
    out='data/btc5m_paper/orders_' + datetime.date.today().isoformat() + '.jsonl'
    with open(out,'a',encoding='utf-8') as f: f.write(json.dumps(rec, ensure_ascii=False)+'\n')
    print(json.dumps({'out':out,'order':rec}, ensure_ascii=False))

if __name__=='__main__': main()
