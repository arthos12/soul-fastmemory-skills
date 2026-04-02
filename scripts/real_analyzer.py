#!/usr/bin/env python3
"""
真正的分析系统 - 归因+推理+预测+验证
"""
import json
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path("data/polymarket")

def load_data():
    results = []
    for f in RESULTS_DIR.glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try: results.append(json.loads(line))
                    except: pass
    return results

def analyze_causation(results):
    """归因: 为什么会这样"""
    print("\n=== 归因分析 ===")
    
    total = len(results)
    high_price = sum(1 for r in results if r.get("curPrice", 0) > 0.7)
    high_pct = high_price/total*100 if total else 0
    
    # 原因推断
    causes = []
    
    # 原因1: 我们的筛选条件可能偏向高概率事件
    causes.append({
        "factor": "筛选条件",
        "hypothesis": "我们倾向于买高概率(>0.7)的事件",
        "evidence": f"高价单占{high_pct:.1f}%",
        "confidence": "高"
    })
    
    # 原因2: BR买的是低概率，我们买的是高概率
    causes.append({
        "factor": "策略方向",
        "hypothesis": "BR买低概率赚差价，我们买高概率",
        "evidence": "BR 62%在<0.02，我们87%在>0.7",
        "confidence": "高"
    })
    
    return causes

def analyze_reasoning(results):
    """推理: 逻辑是什么"""
    print("\n=== 推理分析 ===")
    
    # 我们的策略逻辑
    reasoning = {
        "current": "买高概率事件 → 等结算 → 赚概率差",
        "problem": "高概率意味着低赔率，错了亏更多",
        "br_way": "买低概率 → 快速转手 → 赚波动"
    }
    
    return reasoning

def analyze_prediction(results):
    """预测: 会怎样"""
    print