#!/usr/bin/env python3
import json, urllib.request, datetime, os, re
URL='https://gamma-api.polymarket.com/markets?limit=400&active=true&closed=false'

def get_json(url):
    req=urllib.request.Request(url, headers={'User-Agent':'openclaw/pm-scan'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

def norm_outcomes(v):
    try:
        return json.loads(v) if isinstance(v,str) else v
    except Exception:
        return v

def cls(q):
    ql=q.lower()
    if 'up or down' in ql: return 'updown'
    if any(k in ql for k in ['higher than','above','below','lower than']): return 'threshold'
    if any(k in ql for k in ['close higher','close lower','rise or fall','涨还是跌']): return 'daily_dir'
    return 'other'

def asset(q):
    ql=q.lower()
    for a in ['bitcoin','btc','ethereum','eth','solana','sol','xrp']:
        if a in ql: return a
    return None

def main():
    rows=get_json(URL)
    now=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    out=[]
    for m in rows:
        q=m.get('question') or ''
        a=asset(q)
        if not a: continue
        outcomes=norm_outcomes(m.get('outcomes'))
        prices=norm_outcomes(m.get('outcomePrices'))
        try:
            end=datetime.datetime.fromisoformat((m.get('endDate') or '').replace('Z','+00:00'))
            hrs=(end-now).total_seconds()/3600
        except Exception:
            hrs=None
        out.append({
            'id': m.get('id'), 'question': q, 'slug': m.get('slug'), 'asset': a,
            'type': cls(q), 'hoursToEnd': hrs, 'outcomes': outcomes, 'outcomePrices': prices,
            'url': f"https://polymarket.com/market/{m.get('slug')}" if m.get('slug') else None,
        })
    os.makedirs('data/polymarket', exist_ok=True)
    day=datetime.datetime.utcnow().date().isoformat()
    path=f'data/polymarket/market_scan_{day}.jsonl'
    with open(path,'w',encoding='utf-8') as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False)+'\n')
    print(json.dumps({'out':path,'count':len(out)}, ensure_ascii=False))

if __name__=='__main__': main()
