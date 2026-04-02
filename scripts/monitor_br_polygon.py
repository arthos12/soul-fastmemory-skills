#!/usr/bin/env python3
"""监控BR在Polygon链上的交易"""
import requests
import time
import json

BR_ADDRESS = "0xd84c2b6d65dc596f49c7b6aadd6d74ca91e407b9"

def get_latest_tx():
    """获取BR钱包的最新交易"""
    url = "https://api.polygonscan.com/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": BR_ADDRESS,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": "YourAPIKeyToken"
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "1":
            return data["result"][0]  # 最新交易
    except Exception as e:
        print(f"Error: {e}")
    return None

def monitor(interval=30):
    """持续监控"""
    print(f"=== 监控BR钱包: {BR_ADDRESS} ===")
    print("按Ctrl+C停止\n")
    
    last_tx = get_latest_tx()
    if last_tx:
        print(f"最新交易: {last_tx['hash'][:20]}...")
        print(f"时间: {last_tx['timeStamp']}")
    
    while True:
        time.sleep(interval)
        new_tx = get_latest_tx()
        if new_tx and new_tx != last_tx:
            print(f"\n🆕 新交易!")
            print(f"  Hash: {new_tx['hash']}")
            print(f"  时间: {new_tx['timeStamp']}")
            print(f"  金额: {new_tx['value']}")
            last_tx = new_tx

if __name__ == "__main__":
    monitor()
