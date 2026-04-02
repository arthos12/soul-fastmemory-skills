#!/usr/bin/env python3
import json, urllib.request, statistics, math, datetime, os
BINANCE='https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000'

def get_json(url):
    req=urllib.request.Request(url, headers={'User-Agent':'openclaw/btc5m-sim'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def sim(rows):
    closes=[float(r[4]) for r in rows]
    res=[]
    for i in range(10, len(closes)-5):
        ret5=(closes[i]-closes[i-5])/closes[i-5]
        fut5=(closes[i+5]-closes[i])/closes[i]
        vol5=statistics.pstdev(closes[i-5:i+1])/closes[i] if i>=5 else 0
        if abs(ret5) < 0.0008:
            continue
        mode='trend' if vol5 < 0.0015 else 'meanrev'
        pred = (1 if ret5>0 else -1) if mode=='trend' else (-1 if ret5>0 else 1)
        actual = 1 if fut5>0 else -1
        hit = pred==actual
        # toy market model: binary contract fair payoff 1, entry around 0.5 +/- skew from signal, with cost
        est_p = 0.53 if mode=='trend' else 0.52
        edge = est_p - 0.5
        pnl = (1-0.5-0.01) if hit else (-0.5-0.01)
        res.append({'mode':mode,'ret5':ret5,'fut5':fut5,'hit':hit,'pnl':pnl,'edge':edge})
    return res

def summarize(res):
    out={}
    for mode in ['trend','meanrev']:
        arr=[r for r in res if r['mode']==mode]
        if not arr: continue
        n=len(arr); hit=sum(1 for r in arr if r['hit'])/n; pnl=sum(r['pnl'] for r in arr)
        out[mode]={'n':n,'hit':round(hit,4),'avg_pnl':round(pnl/n,4),'total_pnl':round(pnl,4)}
    n=len(res); hit=sum(1 for r in res if r['hit'])/n if n else 0; pnl=sum(r['pnl'] for r in res)
    out['overall']={'n':n,'hit':round(hit,4),'avg_pnl':round(pnl/n,4) if n else 0,'total_pnl':round(pnl,4)}
    return out

def main():
    rows=get_json(BINANCE)
    res=sim(rows)
    out=summarize(res)
    os.makedirs('data/btc5m_sim', exist_ok=True)
    stamp=datetime.datetime.utcnow().strftime('%F_%H%M%S')
    with open(f'data/btc5m_sim/sim_{stamp}.json','w') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__=='__main__':
    main()
