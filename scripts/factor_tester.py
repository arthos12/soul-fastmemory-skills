#!/usr/bin/env python3
"""
因子测试框架
结合CEX数据 + PM数据 测试因子有效性
"""
import requests, json, time
from datetime import datetime

CEX_SYMBOLS = {'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 'XRP': 'XRPUSDT'}

def get_cex_momentum(symbol, minutes=5):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={minutes}'
    try:
        r = requests.get(url, timeout=5)
        klines = r.json()
        changes = [(float(k[4])-float(k[1]))/float(k[1])*100 for k in klines]
        return sum(changes)/len(changes) if changes else 0
    except:
        return 0

def get_pm_markets(keywords=['bitcoin', 'btc', 'eth', 'sol', 'xrp'], limit=20):
    url = 'https://gamma-api.polymarket.com/markets'
    params = {'closed': 'false', 'limit': limit}
    r = requests.get(url, params=params, timeout=10)
    markets = r.json()
    return [m for m in markets if any(k in m.get('question','').lower() for k in keywords)]

def scan_and_signal():
    print('=== 因子扫描 %s ===' % datetime.now().strftime('%H:%M:%S'))
    
    # CEX动量
    cex = {}
    for name, symbol in CEX_SYMBOLS.items():
        cex[name] = get_cex_momentum(symbol)
    
    print('CEX动量:')
    for k, v in cex.items():
        direction = 'UP' if v > 0 else 'DOWN'
        print('  %s: %.3f%% %s' % (k, v, direction))
    
    # PM市场
    markets = get_pm_markets()
    print('\nPM市场(%d):' % len(markets))
    for m in markets[:5]:
        q = m.get('