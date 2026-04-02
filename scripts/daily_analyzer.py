#!/usr/bin/env python3
"""每日分析系统 - 抓取+分析+调整+验证"""
import json, subprocess, sys, copy
from pathlib import Path
from datetime import datetime

DIRS = {
    "results": Path("data/polymarket"),
    "reports": Path("data/polymarket/reports/strategy_analysis"),
    "strategies": Path("strategies")
}

# BR参考标准
BR_STANDARD = {
    "minPrice": 0.02,      # BR 62%在<0.02
    "maxMinsToEnd": 30,    # BR 5-15分钟
    "target_low_price_pct": 30  # 目标30%低价单
}

def run():
    print(f"=== {datetime.utcnow().isoformat()} 每日分析 ===")
    
    # 1. 抓取
    print("[1/4] 抓取Top Traders...")
    subprocess.run([sys.executable, "scripts/fetch_top_traders.py"], capture_output=True)
    
    # 2. 分析我们
    print("[2/4] 分析我们结果...")
    results = []
    for f in DIRS["results"].glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try: results.append(json.loads(line))
                    except: pass
    
    total = len(results)
    low = sum(1 for r in results if r.get("curPrice", 0) < 0.1)
    high = sum(1 for r in results if r.get("curPrice", 0) > 0.7)
    
    low_pct = low/total*100 if total else 0
    high_pct = high/total*100 if total else 0
    
    print(f"  总单: {total}, 低价<0.1: {low_pct:.1f}%, 高价>0.7: {high_pct:.1f}%")
    
    # 3. 对比差距
    print("[3/4] 对比差距...")
    gaps = []
    if low_pct < 10:
        gaps.append(f"低价单不足: {low_pct:.1f}% vs BR 62%")
    if high_pct > 80:
        gaps.append(f"高价单过多: {high_pct:.1f}% vs BR 12%")
    
    # 4. 自动调整策略
    print("[4/6] 自动调整策略...")
    adjustments = auto_adjust_strategies(gaps)
    if adjustments:
        print(f"  已调整: {len(adjustments)}项")
    else:
        print(f"  已是最佳参数")
    
    # 5. 下单执行
    print("[5/6] 下单执行...")
    order_result = execute_orders()
    
    # 6. 记录
    print("[4/4] 记录日志...")
    log_file = DIRS["reports"] / "ITERATION_LOG.md"
    entry = f"\n## {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC 每日分析\n"
    entry += f"- 总单: {total}, 低价<0.1: {low_pct:.1f}%, 高价>0.7: {high_pct:.1f}%\n"
    if gaps:
        entry += "- 差距:\n"
        for g in gaps:
            entry += f"  - {g}\n"
    if adjustments:
        entry += "- 调整:\n"
        for adj in adjustments:
            entry += f"  - {adj}\n"
    else:
        entry += "- 调整: 无需调整\n"
    entry += "- 状态: 已完成\n"
    
    with open(log_file, "a") as f:
        f.write(entry)
    
    print("=== 完成 ===")
    return {"total": total, "low_pct": low_pct, "high_pct": high_pct, "gaps": gaps}

def auto_adjust_strategies(gaps):
    """自动调整策略参数"""
    adjustments = []
    
    if not gaps:
        return adjustments
    
    # 读取当前策略
    strategy_files = {
        "br_v4_5min_low": DIRS["strategies"] / "br_v4_5min_low.json",
        "sports_event_v1": DIRS["strategies"] / "sports_event_v1.json"
    }
    
    for name, path in strategy_files.items():
        if not path.exists():
            continue
        
        with open(path) as f:
            strategy = json.load(f)
        
        original = copy.deepcopy(strategy)
        
        # 调整min
def execute_orders():
    """执行下单"""
    print("  检查PM runner状态...")
    
    # 记录下单意图
    queue_file = DIRS["reports"] / "order_queue.json"
    queue = []
    if queue_file.exists():
        with open(queue_file) as f:
            queue = json.load(f)
    
    queue.append({
        "ts": datetime.utcnow().isoformat(),
        "strategy": "br_v4_5min_low",
        "action": "run"
    })
    
    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)
    
    return {"queued": len(queue)}

if __name__ == '__main__':
    run()

