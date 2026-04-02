#!/usr/bin/env python3
"""
验证脚本 - 策略有效性 + 因子可靠性
触发条件: 已结算>100单
"""
import json
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path("data/polymarket")

def verify():
    # 加载数据
    results = []
    for f in RESULTS_DIR.glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try: results.append(json.loads(line))
                    except: pass
    
    # 只看已结算
    closed = [r for r in results if r.get("closed")]
    
    if len(closed) < 100:
        print(f"已结算{len(closed)}单，需要>100单才能验证")
        return
    
    print(f"\n=== 验证分析 (已结算{len(closed)}单) ===\n")
    
    # 1. 策略有效性
    total_pnl = sum(r.get("pnl_est", 0) or 0 for r in closed)
    print(f"【策略有效性】")
    print(f"  总PnL: ${total_pnl:+.2f}")
    print(f"  盈利率: {sum(1 for r in closed if (r.get('pnl_est') or 0) > 0)/len(closed)*100:.1f}%")
    
    # 2. 因子可靠性 - 价格
    print(f"\n【因子可靠性 - 价格】")
    price_pnl = defaultdict(lambda: {"count": 0, "pnl": 0})
    for r in closed:
        p = r.get("curPrice", 0)
        pnl = r.get("pnl_est") or 0
        if p < 0.1:
            price_pnl["<0.1"]["count"] += 1
            price_pnl["<0.1"]["pnl"] += pnl
        elif p < 0.5:
            price_pnl["0.1-0.5"]["count"] += 1
            price_pnl["0.1-0.5"]["pnl"] += pnl
        elif p < 0.7:
            price_pnl["0.5-0.7"]["count"] += 1
            price_pnl["0.5-0.7"]["pnl"] += pnl
        else:
            price_pnl[">0.7"]["count"] += 1
            price_pnl[">0.7"]["pnl"] += pnl
    
    print("  价格区间 | 数量 | 总PnL | 单均PnL")
    for range_ in ["<0.1", "0.1-0.5", "0.5-0.7", ">0.7"]:
        d = price_pnl[range_]
        avg = d["pnl"]/d["count"] if d["count"] else 0
        print(f"  {range_:10} | {d['count']:4} | {d['pnl']:+7.2f} | {avg:+7.2f}")
    
    # 结论
    print("\n【结论】")
    best = max(price_pnl.items(), key=lambda x: x[1]["pnl"])
    print(f"  最佳价格区间: {best[0]} (PnL: ${best[1]['pnl']:+.2f})")

if __name__ == "__main__":
    verify()
