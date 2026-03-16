#!/usr/bin/env python3
import json, urllib.request, datetime, os
from math import isnan

URL='https://api.binance.com/api/v3/ticker/24hr'
OUT_DIR='data/crypto_predictions'

def get_json(url):
    req=urllib.request.Request(url, headers={'User-Agent':'openclaw/crypto-pred'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def f(x, d=0.0):
    try: return float(x)
    except: return d

def classify(row):
    qv = f(row.get('quoteVolume'))
    pc = f(row.get('priceChangePercent'))
    wc = abs(pc)
    if qv < 5_000_000: return None
    if wc >= 12: return 'mean_revert'
    if wc >= 4: return 'trend'
    return 'range'

def predict(row, horizon):
    pc = f(row.get('priceChangePercent'))
    hi = f(row.get('highPrice')); lo = f(row.get('lowPrice')); last = f(row.get('lastPrice'))
    rng = (hi-lo)/last if last>0 else 0
    mode = classify(row)
    if mode is None: return None
    if mode == 'mean_revert':
        direction = 'down' if pc>0 else 'up'
        prob = 0.58 if horizon=='4h' else 0.56
    elif mode == 'trend':
        direction = 'up' if pc>0 else 'down'
        prob = 0.57 if horizon=='4h' else 0.59
    else:
        direction = 'range'
        prob = 0.55 if rng < 0.08 else 0.52
    edge_score = prob * min(max(abs(pc)/10,0.4),1.4)
    trade_ok = prob >= 0.57 and mode in ('trend','mean_revert') and abs(pc) >= 4 and f(row.get('quoteVolume')) >= 20_000_000
    return {
        'symbol': row['symbol'], 'lastPrice': last, 'priceChangePercent': pc, 'quoteVolume': f(row.get('quoteVolume')),
        'mode': mode, 'horizon': horizon, 'direction': direction, 'prob': round(prob,4),
        'rangePct': round(rng,4), 'tradeOk': trade_ok, 'edgeScore': round(edge_score,4)
    }

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
    rows = get_json(URL)
    usd = [r for r in rows if r.get('symbol','').endswith('USDT')]
    preds=[]
    for hz in ('4h','24h'):
        for r in usd:
            p = predict(r, hz)
            if p:
                p['createdAt']=now
                preds.append(p)
    preds.sort(key=lambda x:(x['tradeOk'], x['edgeScore'], x['quoteVolume']), reverse=True)
    out = os.path.join(OUT_DIR, f'predictions_{datetime.date.today().isoformat()}.jsonl')
    with open(out,'w',encoding='utf-8') as f:
        for p in preds[:120]:
            f.write(json.dumps(p, ensure_ascii=False)+'\n')
    trades = [p for p in preds if p['tradeOk']][:20]
    trades_out = os.path.join(OUT_DIR, f'trade_candidates_{datetime.date.today().isoformat()}.jsonl')
    with open(trades_out,'w',encoding='utf-8') as f:
        for p in trades:
            f.write(json.dumps(p, ensure_ascii=False)+'\n')
    print(json.dumps({'predictions': min(len(preds),120), 'tradeCandidates': len(trades), 'predFile': out, 'tradeFile': trades_out}, ensure_ascii=False))

if __name__=='__main__':
    main()
