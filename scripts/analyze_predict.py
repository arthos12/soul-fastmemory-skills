#!/usr/bin/env python3
"""
分析 + 预测结合系统
分析过去 → 预测未来 → 决策 → 验证
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

RESULTS_DIR = Path("data/polymarket")
LOG_FILE = Path("data/polymarket/reports/strategy_analysis/ITERATION_LOG.md")

def load_recent_data(hours=24):
    """加载最近N小时的数据"""
    results = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    for f in RESULTS_DIR.glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try:
                        r = json.loads(line)
                        # 检查时间
                        ts = r.get("ts_checked", 0)
                        if ts > cutoff.timestamp():
                            results.append(r)
                    except:
                        pass
    return results

def analyze(results):
    """分析: 发生了什么"""
    if not results:
        return {"error": "无数据"}
    
    total = len(results)
    closed = sum(1 for r in results if r.get("closed"))
    
    # 价格分布
    price_ranges = {"<0.02": 0, "0.02-0.1": 0, "0.1-0.5": 0, "0.5-0.7": 0, ">0.7": 0}
    for r in results:
        p = r.get("curPrice", 0)
        if p < 0.02: price_ranges["<0.02"] += 1
        elif p < 0.1: price_ranges["0.02-0.1"] += 1
        elif p < 0.5: price_ranges["0.1-0.5"] += 1
        elif p < 0.7: price_ranges["0.5-0.7"] += 1
        else: price_ranges
