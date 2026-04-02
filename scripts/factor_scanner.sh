#!/bin/bash
# 因子扫描脚本 - 每5分钟运行
echo "=== 因子扫描 $(date) ==="

python3 << 'EOF'
import requests, json
from datetime import datetime

print('时间:', datetime.now().strftime('%H:%M:%S'))

# 因子1: CEX动量
cex = {}
for sym, name in [('BTCUSDT','BTC'), ('ETHUSDT','ETH'), ('SOLUSDT','SOL'), ('XRPUSDT','XRP')]:
    url = f'https://api.binance.com/api/v3/klines?symbol={sym}&interval=1m&limit=5'
    try:
        r = requests.get(url, timeout=5)
        klines = r.json()
        avg = sum((float(k[4])-float(k[1]))/float(k[1])*100 for k in klines)/5
        cex[name] = avg
    except:
        cex[name] = 0

print('CEX动量:', {k: '%.2f%%' % v for k,v in cex.items()})

# 因子2: PM市场
url = 'https://gamma-api.polymarket.com/markets?closed=false&limit=50'
r = requests.get(url, timeout=10)
markets = r.json()

# 找Crypto + 低价
signals = []
for m in markets:
    q = m.get('question', '')
    prices = m.get('outcomePrices', [])
    liq = m.get('liquidityNum', 0)
    
    if not prices or not isinstance(prices, list):
        continue
        
    try:
        min_p = min(float(p) for p in prices)
        # 过滤: Crypto + 低价 + 高流动性
        q_lower = q.lower()
        is_crypto = any(x in q_lower for x in ['bitcoin','btc','eth','sol','xrp'])
        
        if is_crypto and min_p < 0.3 and liq > 10000:
            signals.append({
                'question': q[:50],
                'min_price': min_p,
