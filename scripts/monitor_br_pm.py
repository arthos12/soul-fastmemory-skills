#!/usr/bin/env python3
"""监控BR在PM的交易"""
import requests
import time

LAST_TS = 0

def get_br_trades():
    url = "https://data-api.polymarket.com/trades?user=BoneReader&limit=5"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        return r.json()
    return []

def check_new():
    global LAST_TS
    trades = get_br_trades()
    if not trades:
        return
    
    latest = trades[0]
    ts = latest.get("timestamp", 0)
    
    if ts > LAST_TS:
        LAST_TS = ts
        print(f"\n🆕 BR新交易!")
        print(f"  时间: {time.strftime('%H:%M:%S', time.localtime(ts))}")
        print(f"  品种: {latest.get('title', '')[:40]}")
        print(f"  方向: {latest.get('side')} {latest.get('outcome')}")
        print(f"  价格: {latest.get('price')}")
        return True
    return False

if __name__ == "__main__":
    print("=== 监控BR交易 ===")
    print("按Ctrl+C停止\n")
    
    while True:
        check_new()
        time.sleep(10)  # 每10秒检查
