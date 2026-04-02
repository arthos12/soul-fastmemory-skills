#!/usr/bin/env python3
"""量化工作启动清单 - 自动检查"""
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 50)
    print(f"量化检查 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. Runner
    print("\n【1. Runner】")
    r = subprocess.run("ps aux | grep pm_auto | grep -v grep", shell=True, capture_output=True)
    print(f"  状态: {'✅ 运行中' if r.stdout else '❌ 未运行'}")
    
    # 2. 订单
    print("\n【2. 订单】")
    orders = list(Path("data/polymarket").glob("paper_orders_*.jsonl"))
    today = [f for f in orders if "2026-03-20" in f.name]
    print(f"  今日: {len(today)}个文件")
    
    # 3. 策略
    print("\n【3. 策略】")
    s = Path("strategies/br_v4_5min_low.json")
    if s.exists():
        import json
        d = json.loads(s.read_text())
        print(f"  minPrice: {d.get('minPrice')} (目标<0.02)")
        print(f"  maxMinsToEnd: {d.get('maxMinsToEnd')} (目标<30)")
    
    # 4. 数据
    print("\n【4. 数据】")
    results = []
    for f in Path("data/polymarket").glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            for line in f:
                try: results.append(eval(line))
                except: pass
    closed = sum(1 for r in results if r.get("closed"))
    print(f"  总单: {len(results)}")
    print(f"  已结算: {closed}")
    
    # 5. 定时
    print("\n【5. 定时任务】")
    c = subprocess.run("crontab -l | grep hourly