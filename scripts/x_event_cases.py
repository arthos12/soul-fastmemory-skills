#!/usr/bin/env python3
import argparse, json, os, re, datetime
TIME_PAT=re.compile(r'\b(today|tomorrow|this week|this month|by\b|before\b|at \d{1,2}:\d{2}|\d+h|\d+ hours?)\b', re.I)

def classify(txt):
    t=txt.lower()
    if any(k in t for k in ['will list','listing','launch','release','debut','approve','approval','vote','decision']):
        return 'direct_event'
    if any(k in t for k in ['buy','sold','inflows','outflows','raised','$btc','$eth']):
        return 'market_signal'
    if any(k in t for k in ['breaking','warns','minister says','statement','strike','ceasefire']):
        return 'macro_event'
    return 'other'

def score(r):
    txt=(r.get('title','')+' '+r.get('text',''))
    s=0
    if r.get('author') in ['WuBlockchain','lookonchain','unusual_whales','tier10k']: s+=2
    if TIME_PAT.search(txt): s+=3
    if r.get('checkableCandidate'): s+=2
    c=classify(txt)
    if c=='direct_event': s+=4
    elif c=='market_signal': s+=2
    elif c=='macro_event': s+=1
    if 'will list' in txt.lower(): s+=4
    return s,c

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=10)
    args=ap.parse_args()
    rows=[]
    for line in open(args.inp,encoding='utf-8'):
        if not line.strip(): continue
        r=json.loads(line)
        if r.get('error'): continue
        s,c=score(r)
        if s < 4: continue
        txt=(r.get('title','')+' '+r.get('text',''))
        tw='24h' if re.search(r'today|24h|hours?|at \d{1,2}:\d{2}', txt, re.I) else ('7d' if re.search(r'this week', txt, re.I) else '3d')
        rows.append({
            'createdAt': datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z',
            'platform':'X','author':r.get('author'),'url':r.get('url'),'publishedAt':r.get('publishedAt'),
            'title':r.get('title'),'eventType':c,'score':s,'timeWindow':tw,
            'claim':r.get('title'),'status':'PREDICT_READY','actualResult':None
        })
    rows.sort(key=lambda x:(x['score'],x['publishedAt']), reverse=True)
    rows=rows[:args.limit]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,'w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
    print(json.dumps({'cases': len(rows), 'out': args.out}, ensure_ascii=False))

if __name__=='__main__':
    main()
