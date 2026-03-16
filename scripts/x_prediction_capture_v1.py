#!/usr/bin/env python3
import json, os, datetime

OUT='data/x_predictions/cases_2026-03-16_v1.jsonl'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# v1: bootstrap with manually structured case slots so capture can start immediately.
# Real source expansion can replace this, but the case format and pipeline start now.
seed_cases = [
  {
    'source': 'x',
    'status': 'capture_schema_ready',
    'targetType': 'crypto_price',
    'platform': 'X',
    'author': None,
    'url': None,
    'symbol': 'BTCUSDT',
    'claim': '24h direction prediction slot',
    'timeWindow': '24h',
    'checkable': True,
    'needsSourceFill': True,
  },
  {
    'source': 'x',
    'status': 'capture_schema_ready',
    'targetType': 'crypto_price',
    'platform': 'X',
    'author': None,
    'url': None,
    'symbol': 'ETHUSDT',
    'claim': '24h direction prediction slot',
    'timeWindow': '24h',
    'checkable': True,
    'needsSourceFill': True,
  },
  {
    'source': 'x',
    'status': 'capture_schema_ready',
    'targetType': 'event',
    'platform': 'X',
    'author': None,
    'url': None,
    'symbol': None,
    'claim': 'short-window event prediction slot',
    'timeWindow': '3d',
    'checkable': True,
    'needsSourceFill': True,
  }
]
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
with open(OUT,'w',encoding='utf-8') as f:
    for c in seed_cases:
        c['createdAt']=now
        f.write(json.dumps(c, ensure_ascii=False)+'\n')
print(json.dumps({'file': OUT, 'cases': len(seed_cases), 'status': 'started'}, ensure_ascii=False))
