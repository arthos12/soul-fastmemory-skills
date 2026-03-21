#!/usr/bin/env python3
"""主动分析系统"""
import json
from pathlib import Path

TOP_TRADERS_DIR = Path("data/polymarket/top_traders")
RESULTS_DIR = Path("data/polymarket")

def load_our_results():
    results = []
    for f in RESULTS_DIR.glob("paper_results_*.jsonl"):
        if f.stat().st_size > 100:
            with open(f) as fp:
                for line in fp:
                    try: results.append(json.loads(line))
                    except: pass
    return results

def analyze():
    results = load_our_results()
    total = len(results)
    closed = sum(1 for r in results if r.get("closed"))
    
    prices = {"<0.1": 0, "0.1-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, ">0.7": 0}
    for r in results:
        p = r.get("curPrice", 0)
        if p < 0.1: prices["<0.1"] += 1
        elif p < 0.3: prices["0.1-0.3"] += 1
        elif p < 0.5: prices["0.3-0.5"] += 1
        elif p < 0.7: prices["0.5-0.7"] += 1
        else: prices[">0.7"] += 1
    
    print(f"总单数: {total}, 已结算: {closed}")
    if total == 0:
        print("低价单(<0.1): 0 (0.0%)")
    else:
        print(f"低价单(<0.1): {prices['<0.1']} ({prices['<0.1']/total*100:.1f}%)")
    print(f"对比BR: 62%在<0.02")

if __name__ == "__main__":
    analyze()
