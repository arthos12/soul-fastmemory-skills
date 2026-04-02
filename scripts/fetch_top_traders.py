#!/usr/bin/env python3
"""
自动抓取Top Traders数据
"""
import re
import json
import requests
from pathlib import Path
from datetime import datetime

TOP_TRADERS = [
    "HorizonSplendidView",
    "reachingthesky", 
    "majorexploiter",
    "BoneReader"
]

def fetch_profile(username):
    """从PM获取用户数据"""
    url = f"https://polymarket.com/profile/%40{username}"
    
    try:
        html = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0'
        }, timeout=20).text
        
        # 提取__NEXT_DATA__
        match = re.search(r'__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if not match:
            return None
            
        obj = json.loads(match.group(1))
        queries = obj['props']['pageProps']['dehydratedState']['queries']
        
        return {
            "fetchedAt": datetime.utcnow().isoformat() + "Z",
            "profileUrl": url,
            "queryCount": len(queries),
            "username": username
        }
    except Exception as e:
        print(f"Error fetching {username}: {e}")
        return None

def main():
    out_dir = Path("data/polymarket/top_traders")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=== 抓取 {len(TOP_TRADERS)} 个Top Traders ===")
    
    for username in TOP_TRADERS:
        print(f"抓取 {username}...")
        data = fetch_profile(username)
        
        if data:
            out_file = out_dir / f"{username.lower()}_structured.json"
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  ✓ 保存到 {out_file}")
    
    print("=== 完成 ===")

if __name__ == "__main__":
    main()
