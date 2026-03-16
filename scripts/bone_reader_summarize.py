#!/usr/bin/env python3
import json, os, statistics
p='data/polymarket/bone_reader_profile_dump.json'
d=json.load(open(p))['queryMap']
res={}
for k,v in d.items():
    if '"/api/profile/volume"' in k: res['volume']=v
    elif '"user-stats"' in k: res['user_stats']=v
    elif '"portfolio-pnl"' in k:
        if '"1D"' in k: res['pnl_1d']=v
        elif '"1W"' in k: res['pnl_1w']=v
        elif '"1M"' in k: res['pnl_1m']=v
        elif '"ALL"' in k: res['pnl_all']=v
# summarize curves
for key in ['pnl_1d','pnl_1w','pnl_1m','pnl_all']:
    arr=res.get(key) or []
    if not arr: continue
    vals=[x['p'] for x in arr]
    res[key+'_summary']={
        'points': len(vals), 'start': vals[0], 'end': vals[-1], 'delta': vals[-1]-vals[0],
        'max': max(vals), 'min': min(vals),
    }
out='data/polymarket/bone_reader_summary.json'
json.dump(res, open(out,'w'), ensure_ascii=False, indent=2)
print(out)
