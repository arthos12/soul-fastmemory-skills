#!/usr/bin/env python3
"""
定时市场扫描脚本
每5分钟扫描一次，发现低概率高成交量机会
"""

import json
import requests
import time
from datetime import datetime

def scan_opportunities():
    """扫描市场机会"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 100}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        markets = resp.json()
    except:
        return []
    
    opportunities = []
    for m in markets:
        try:
            prices = json.loads(m.get('outcomePrices', '[]'))
            vol = float(m.get('volume', 0))
            if prices and float(prices[0]) < 0.3 and vol > 50000:
                opportunities.append({
                    'question': m.get('question', '')[:50],
                    'p_yes': float(prices[0]),
                    'volume': vol,
                    'time': datetime.now().strftime('%H:%M')
                })
        except:
            continue
    
    return opportunities

def main():
    """主循环：每5分钟扫描一次"""
    print("市场扫描启动 | 每5分钟运行")
    
    while True:
        opps = scan_opportunities()
        if opps:
            opps.sort(key=lambda x: -x['volume'])
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(opps)} 个机会:")
            for i, o in enumerate(opps[:3]):
                print(f"  {i+1}. {o['question']} | P={o['p_yes']:.2f} | V=${o['volume']:,.0f}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 无新机会")
        
        time.sleep(300)  # 5分钟

if __name__ == "__main__":
    main()
