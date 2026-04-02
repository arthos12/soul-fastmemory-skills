#!/usr/bin/env python3
"""
从Polyscan抓取BR完整交易历史
目标: 2000+条数据
"""
import requests
import json
import time
from pathlib import Path

BR_WALLET = "0xd84c2b6d65dc596f49c7b6aadd6d74ca91e407b9"
POLYSCAN_API = "https://api.polygonscan.com/api"

# 存储位置
OUTPUT_DIR = Path("data/polymarket/top_traders/br")
OUTPUT_FILE = OUTPUT_DIR / "transactions_2000.json"

def fetch_transactions(offset=0, limit=100):
    """从Polyscan API获取交易"""
    params = {
        "module": "account",
        "action": "tokentx",
        "address": BR_WALLET,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": "YourAPIKeyToken"  # 免费API key
    }
    
    try:
        r = requests.get(POLYSCAN_API, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "1":
            return data.get("result", [])
    except Exception as e:
        print(f"Error: {e}")
    return []

def main():
    print(f"=== 抓取BR交易历史 ===")
    print(f"目标: 2000条")
    print(f"钱包: {BR_WALLET}")
    
    all_tx = []
    offset = 0
    
    # 先尝试不用API key
    print("\n尝试获取...")
    
    # 由于Polyscan API需要key，先用网页抓取
    print("\n需要Polyscan API key才能获取完整数据")
    print("或使用浏览器手动抓取")
    
if __name__ == "__main__":
    main()
