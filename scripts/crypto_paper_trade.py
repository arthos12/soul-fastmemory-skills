#!/usr/bin/env python3
import argparse, json, os, datetime

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--max-orders', type=int, default=20)
    ap.add_argument('--stake', type=float, default=1000.0)
    args=ap.parse_args()
    rows=[]
    with open(args.inp,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip(): rows.append(json.loads(line))
    rows=[r for r in rows if r.get('tradeOk')][:args.max_orders]
    now=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,'w',encoding='utf-8') as f:
        for r in rows:
            rec={
                'createdAt': now,
                'symbol': r['symbol'],
                'horizon': r['horizon'],
                'direction': r['direction'],
                'prob': r['prob'],
                'edgeScore': r['edgeScore'],
                'referencePrice': r['lastPrice'],
                'stake': args.stake,
                'status': 'OPEN',
                'resultCheckDueAt': now,
                'sourceFile': args.inp,
            }
            f.write(json.dumps(rec, ensure_ascii=False)+'\n')
    print(json.dumps({'orders': len(rows), 'out': args.out}, ensure_ascii=False))

if __name__=='__main__':
    main()
