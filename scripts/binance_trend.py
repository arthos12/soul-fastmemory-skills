#!/usr/bin/env python3
"""币安趋势检查"""
import requests
import time

def get_price(symbol="BTCUSDT"):
    """获取当前价格"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        return float(r.json()["price"])
    return None

def get_klines(symbol="BTCUSDT", interval="1m", limit=5):
    """获取K线数据"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url, timeout=5)
    if r.status_code == 200:
        data = r.json()
        # 返回收盘价列表
        return [float(c[4]) for c in data]
    return None

def is_trending_up(symbol="BTCUSDT"):
    """检查是否在上涨趋势"""
    prices = get_klines(symbol, "1m", 5)
    if not prices or len(prices) < 3:
        return False
    
    # 最近3个1分钟K线
    recent = prices[-3:]
    
    # 简单判断: 3根K线整体上涨
    if recent[-1] > recent[0]:
        return True
    return False

def check_any_uptrend(symbols):
    """检查任一币种是否上涨"""
    for sym in symbols:
        if is_trending_up(sym):
            return True, sym
    return False, None

if __name__ == "__main__":
    # 测试
    for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]:
        price = get_price(sym)
        trend = is_trending_up(sym)
        print(f"{sym}: ${price:.2f} 趋势: {'↑' if trend else '↓'}")
