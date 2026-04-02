#!/bin/bash
# 因子扫描 - 每5分钟运行
# 数据来源: ours (我们的模拟)

cd /root/.openclaw/workspace

python3 << 'PYEOF'
import requests, json
from datetime import datetime

LOG_FILE = 'data/polymarket/ours/factor_scan.log'

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{datetime.now().isoformat()} {msg}\n')

print('=== 因子扫描 %s ===' % datetime.now().strftime('%H:%M'))

# 因子1: CEX动量
cex_mom = {}
for name, sym in [('BTC','BTCUSDT'), ('ETH','ETHUSDT'), ('SOL','SOLUSDT'), ('XRP','XRPUSDT')]:
    try:
        url = f'https://api.binance.com/api/v3/klines?symbol={sym}&interval=1m&limit=5'
        r = requests.get(url, timeout=5)
        klines = r.json()
        mom = sum((float(k[4])-float(k[1]))/float(k[1])*100 for k in klines)/5
        cex_mom[name] = mom
    except:
        cex_mom[name] = 0

print('CEX动量:', {k:'%.3f%%' % v for k,v in cex_mom.items()})
log('CEX动量: %s' % cex_mom)

# 因子2: CEX成交量突变
for name, sym in [('BTC','BTCUSDT'), ('SOL','SOLUSDT')]:
    try:
        url = f'https://api.binance.com/api/v3/klines?symbol={sym}&interval=1m&limit=10'
        r = requests.get(url, timeout=5)
        klines = r.json()
        vols = [float(k[5]) for k in klines]
        ratio = sum(vols[-3:])/3 / (sum(vols[:-3])/7) if sum(vols[:-3])>0 else 1
        print('Vol %s