#!/usr/bin/env python3
"""大行情分析 - 多维度市场数据"""
import requests

def get_ticker(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url, timeout=5)
    return r.json() if r.status_code == 200 else None

def get_klines(symbol, interval, limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        return [float(c[4]) for c in data]
    return None

def analyze_trend(prices):
    if not prices or len(prices) < 10:
        return "数据不足"
    recent = prices[-10:]
    start = sum(recent[:5]) / 5
    end = sum(recent[-5:]) / 5
    change = (end - start) / start * 100
    if change > 2:
        return "上涨"
    elif change < -2:
        return "下跌"
    return "震荡"

def main():
    print("="*60)
    print("大行情分析报告")
    print("="*60)
    
    symbols = {
        "BTCUSDT": "比特币",
        "ETHUSDT": "以太坊", 
        "SOLUSDT": "Solana",
        "XRPUSDT": "XRP"
    }
    
    results = {}
    for symbol, name in symbols.items():
        print(f"\n【{name}】")
        
        # 24小时数据
        ticker = get_ticker(symbol)
        if ticker:
            price = float(ticker["lastPrice"])
            change = float(ticker["priceChangePercent"])
            volume = float(ticker["quoteVolume"])
            print(f"  价格: ${price:.2f}")
            print(f"  24h涨跌: {change:+.2f}%")
            print(f"  24h成交量: ${volume/1e9:.2f}B")
        
        #