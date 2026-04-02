#!/usr/bin/env python3
"""
市场状态识别模块
功能：基于ATR和ADX判断市场状态
"""

import json
import requests
from datetime import datetime, timedelta

def get_recent_markets(limit=50):
    """获取最近的市场数据"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": limit}
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def calculate_volatility(markets):
    """计算市场波动率"""
    if not markets:
        return 0
    
    prices = []
    for m in markets:
        try:
            if m.get('outcomePrices'):
                outcome_prices = json.loads(m['outcomePrices'])
                for p in outcome_prices:
                    price = float(p)
                    if price > 0.01:  # 过滤极端值
                        prices.append(price)
        except:
            continue
    
    if not prices:
        return 0
    
    # 简单波动率：价格标准差
    mean = sum(prices) / len(prices)
