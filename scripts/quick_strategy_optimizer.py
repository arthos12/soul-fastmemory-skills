#!/usr/bin/env python3
"""
快速策略优化器
立即执行策略优化迭代，严格控制token使用
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_strategies():
    """备份策略"""
    print("备份当前策略...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"strategies/versions/{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file in Path("strategies").glob("*.json"):
        if file.name != "strategy_registry.json":
            shutil.copy2(file, backup_dir / file.name)
    
    print(f"  备份到: {backup_dir}")
    return backup_dir

def analyze_strategy(strategy_name):
    """分析策略"""
    file_path = Path(f"strategies/{strategy_name}.json")
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        config = json.load(f)
    
    # 分析配置
    analysis = {
        "name": strategy_name,
        "min_price": config.get("minPrice", 1.0),
        "keywords_count": len(config.get("keywords", [])),
        "size_usd": config.get("sizeUSD", 0),
        "dedup_hours": config.get("dedupLookbackHours", 6),
        "max_orders": config.get("maxOrders", 40),
        "require_accepting": config.get("requireAcceptingOrders", False)
    }
    
    return analysis

def generate_optimization(analysis):
    """生成优化方案"""
    changes = []
    
    # BR标准参考
    br_standards = {
        "min_price": 0.5,
        "min_keywords": 5,
        "size_usd": 50,
        "dedup_hours": 6,
        "max_orders": 40
    }
    
    # 1. 价格过滤优化
    if analysis["min_price"] > br_standards["min_price"] + 0.1:
        changes.append({
            "parameter": "minPrice",
            "action": "decrease",
            "from": analysis["min_price"],
            "to": br_standards["min_price"],
            "reason": "降低到BR标准价格"
        })
    
    # 2. 关键词优化
    if analysis["keywords_count"] < br_standards["min_keywords"]:
        changes.append({
            "parameter": "keywords",
            "action": "add",
            "from": analysis["keywords_count"],
            "to": f"至少{br_standards['min_keywords']}个",
            "reason": "增加关键词数量"
        })
    
    # 3. 仓位优化
    if analysis["size_usd"] == 0:
        changes.append({
            "parameter": "sizeUSD",
            "action": "set",
            "from": analysis["size_usd"],
            "to": br_standards["size_usd"],
            "reason": "设置标准仓位"
        })
    
    # 限制变化数量
    return changes[:2]  # 最多2个变化

def apply_optimization(strategy_name, changes):
    """应用优化"""
    file_path = Path(f"strategies/{strategy_name}.json")
    with open(file_path, 'r') as f:
        config = json.load(f)
    
    original_config = config.copy()
    
    # 应用变化
    applied = []
    for change in changes:
        param = change["parameter"]
        
        if param == "minPrice":
            config["minPrice"] = change["to"]
            applied.append(f"minPrice: {change['from']}→{change['to']}")
        
        elif param == "keywords":
            # 添加基础关键词
            current = set(config.get("keywords", []))
            basic_keywords = {"bitcoin", "btc", "ethereum", "eth", "solana", "sol"}
            config["keywords"] = list(current | basic_keywords)
            applied.append(f"keywords: +{len(basic_keywords - current)}个")
        
        elif param == "sizeUSD":
            config["sizeUSD"] = change["to"]
            applied.append(f"sizeUSD: {change['from']}→{change['to']}")
    
    # 创建优化版本
    version_suffix = datetime.now().strftime("%y%m%d_%H%M")
    optimized_name = f"{config.get('name', strategy_name)}_opt_{version_suffix}"
    config["name"] = optimized_name
    config["optimized_from"] = strategy_name
    config["optimization_date"] = datetime.now().isoformat()
    config["changes_applied"] = applied
    
    # 保存优化版本
    optimized_dir = Path("strategies/optimized")
    optimized_dir.mkdir(exist_ok=True)
    
    output_file = optimized_dir / f"{strategy_name}_opt_{version_suffix}.json"
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # 也更新原文件（可选）
    # with open(file_path, 'w') as f:
    #     json.dump(config, f, indent=2)
    
    return output_file, applied

def main():
    """主函数"""
    print("快速策略优化迭代")
    print("="*70)
    
    # 1. 备份
    backup_dir = backup_strategies()
    
    # 2. 选择优化目标
    strategies = []
    for file in Path("strategies").glob("*.json"):
        if file.name != "strategy_registry.json" and "cex" not in file.name.lower():
            strategies.append(file.stem)
    
    # 优先优化高概率和宽松策略
    targets = []
    for s in strategies:
        if "highprob" in s or "relaxed" in s or "short" in s:
            targets.append(s)
    
    targets = targets[:3]  # 最多3个
    print(f"\n优化目标: {targets}")
    
    # 3. 执行优化
    optimized_files = []
    
    for target in targets:
        print(f"\n优化策略: {target}")
        print("-"*40)
        
        # 分析
        analysis = analyze_strategy(target)
        if not analysis:
            print("  分析失败，跳过")
            continue
        
        print(f"  当前配置:")
        print(f"    minPrice: {analysis['min_price']}")
        print(f"    关键词数: {analysis['keywords_count']}")
        print(f"    sizeUSD: {analysis['size_usd']}")
        
        # 生成优化
        changes = generate_optimization(analysis)
        if not changes:
            print("  无需优化，配置合理")
            continue
        
        print(f"  优化建议:")
        for change in changes:
            print(f"    - {change['reason']}: {change['parameter']} {change['from']}→{change['to']}")
        
        # 应用优化
        output_file, applied = apply_optimization(target, changes)
        optimized_files.append(output_file)
        
        print(f"  优化完成:")
        for a in applied:
            print(f"    ✓ {a}")
        print(f"  保存到: {output_file}")
    
    # 4. 生成报告
    print("\n" + "="*70)
    print("优化完成报告")
    print("="*70)
    
    if optimized_files:
        print(f"成功优化 {len(optimized_files)} 个策略:")
        for file in optimized_files:
            print(f"  ✓ {file.name}")
        
        print("\n下一步:")
        print("1. 测试优化后的策略:")
        print(f"   python3 scripts/pm_paper_loop.py --strategy {optimized_files[0].stem}")
        print("\n2. 监控token使用:")
        print("   python3 scripts/universal_cache_optimizer.py --stats")
        print("\n3. 对比优化前后:")
        print("   diff strategies/versions/{backup_dir.name}/ strategies/")
    else:
        print("未进行优化，所有策略配置合理")
    
    print("\n" + "="*70)
    print("✅ 策略优化迭代完成")
    print("严格控制token使用，谨慎添加策略版本")
    print("="*70)

if __name__ == "__main__":
    main()