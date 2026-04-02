#!/usr/bin/env python3
"""
BR策略模拟回测
模拟BR的5分钟超短线策略
"""

import random
import json
from datetime import datetime, timedelta

def generate_mock_klines(days=7, interval_minutes=5):
    """生成模拟的5分钟K线数据"""
    klines = []
    now = datetime.now()
    
    # 模拟每天的交易时段（16小时）
    minutes_per_day = 16 * 60
    total_klines = (minutes_per_day // interval_minutes) * days
    
    for i in range(total_klines):
        # 开盘价：70%概率是0-0.2（接近0），30%概率是随机
        if random.random() < 0.7:
            open_price = random.uniform(0, 0.2)
        else:
            open_price = random.uniform(0.1, 0.9)
        
        # 波动：开盘后价格波动
        change = random.uniform(-0.3, 0.8)
        close_price = max(0.001, open_price + change)
        
        klines.append({
            'time': (now - timedelta(minutes=total_klines*5 - i*5)).isoformat(),
            'open': round(open_price, 4),
            'close': round(close_price, 4),
            'high': round(max(open_price, close_price) * random.uniform(1.0, 1.2), 4),
            'low': round(min(open_price, close_price) * random.uniform(0.8, 1.0), 4)
        })
    
    return klines

def simulate_br_strategy(klines, buy_threshold=0.1, sell_threshold=0.5):
    """模拟BR策略：买入条件=开盘价<buy_threshold，卖出条件=收盘价>sell_threshold"""