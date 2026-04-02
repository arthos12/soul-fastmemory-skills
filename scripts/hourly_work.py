#!/usr/bin/env python3
"""每小时工作: 检查 + 分析 + 迭代"""
import subprocess, json
from pathlib import Path
from datetime import datetime

def main():
    print(f"\n{'='*50}")
    print(f"每小时工作 - {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    # 1. 检查
    print("\n【检查】软件运行")
    r = subprocess.run("ps aux | grep pm_auto | grep -v grep", shell=True, capture_output=True)
    print(f"  Runner: {'✅' if r.stdout else '❌'}")
    
    s = Path("strategies/br_v4_5min_low.json")
    if s.exists():
        d = json.loads(s.read_text())
        print(f"  minPrice: {d.get('minPrice')} {'✅' if d.get('minPrice')<=0.02 else '❌'}")
        print(f"  maxMinsToEnd: {d.get('maxMinsToEnd')} {'✅' if d.get('maxMinsToEnd')<=30 else '❌'}")
    
    # 2. 分析
    print("\n【分析】数据分析")
    results = []
    for f in Path("data/polymarket").glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            for line in open(f):
                try: results.append(eval(line))
                except: pass
    
    total = len(results)
    closed = sum(1 for r in results if r.get("closed"))
    print(f"  总单: {total}, 已结算: {closed}")
    
    # 3. 迭代
    print("\n【迭代】策略调整")
    gaps = []
    high = sum(1 for r in results if r.get("curPrice", 0) > 0.7)
    if total > 0 and high/total > 0.8:
        gaps.append("高价单过多")
    
    if gaps:
        print(f"  发现: {gaps[0]}")
    else:
        print("  无需调整 ✅")
    
    # 4. 记忆压缩检查
    print("\n【记忆】压缩检查")
    try:
        r = subprocess.run(
            ["python3", "scripts/auto_compactor.py", "--check-only"],
            capture_output=True, text=True, timeout=30
        )
        # 提取关键行输出
        for line in r.stdout.split("\n"):
            if "超长文件" in line or "需要合并" in line or "✅" in line or "⚠️" in line:
                print(f"  {line.strip()}")
    except Exception as e:
        print(f"  压缩检查跳过: {e}")

    # 5. 验证触发
    if closed > 100:
        print(f"  已结算{closed}单 → 触发验证")
        # TODO: 调用验证脚本
    else:
        print(f"  已结算{closed}单 → 需要>{100-closed}单触发验证")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    main()
def count_order_rate():
    """统计每日下单率"""
    from pathlib import Path
    from collections import defaultdict
    
    results = list(Path("data/polymarket").glob("paper_results_*.jsonl"))
    
    # 按日期统计
    by_date = defaultdict(int)
    for f in results:
        if f.stat().st_size > 100:
            name = f.name
            for part in name.split("_"):
                if part.startswith("2026-03-"):
                    count = sum(1 for line in open(f) if line.strip())
                    by_date[part[:10]] += count
                    break
    
    # 今日
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")[:10]
    today_count = by_date.get("2026-03-20", 0)
    checks = 72  # 约6小时 × 12次
    
    print(f"\n【下单率】")
    print(f"  今日下单: {today_count}单")
    print(f"  检查次数: ~{checks}次")
    print(f"  每check: {today_count/checks:.1f}单")
    

