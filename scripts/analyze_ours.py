#!/usr/bin/env python3
"""分析我们自己的结果"""
import json
from pathlib import Path

RESULTS_DIR = Path("data/polymarket")

def load_our_results():
    results = []
    for f in RESULTS_DIR.glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try:
                        results.append(json.loads(line))
                    except:
                        pass
    return results

def analyze():
    results = load_our_results()
    if not results:
        print("无结果数据")
        return
    
    # 基础统计
    total = len(results)
    closed = sum(1 for r in results if r.get("closed"))
    pending = total - closed
    
    # 按策略
    strategies = {}
    for r in results:
        s = r.get("strategy_version", "unknown")
        strategies[s] = strategies.get(s, 0) + 1
    
    # 按价格区间
    prices = {"<0.1": 0, "0.1-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, ">0.7": 0}
    for r in results:
        p = r.get("curPrice", 0)
        if p < 0.1: prices["<0.1"] += 1
        elif p < 0.3: prices["0.1-0.3"] += 1
        elif p < 0.5: prices["0.3-0.5"] += 1
        elif p < 0.7: prices["0.5-0.7"] += 1
        else: prices[">0.7"] += 1
    
    print(f"=== 我们自己的结果分析 ===")
    print(f"总单数: {total}")
    print(f"已结算: {closed}")
    print(f"待结算: {pending}")
    print(f"")
    print(f"### 按策略")
    for s, c in sorted(strategies.items(), key=lambda x: -x[1]):
        print(f"  {s}: