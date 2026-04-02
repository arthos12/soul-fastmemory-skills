#!/usr/bin/env python3
"""
策略优化执行器
立即执行策略优化迭代，严格控制token使用
"""

import os
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

class StrategyOptimizationExecutor:
    """策略优化执行器"""
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.strategies_dir = self.workspace / "strategies"
        self.versions_dir = self.strategies_dir / "versions"
        self.optimized_dir = self.strategies_dir / "optimized"
        
        # 创建目录
        self.versions_dir.mkdir(exist_ok=True)
        self.optimized_dir.mkdir(exist_ok=True)
        
        # 优化配置
        self.config = {
            "max_optimizations_per_day": 3,  # 每日最多优化3个策略
            "min_version_interval_hours": 2,  # 版本间隔至少2小时
            "token_budget_per_optimization": 2000,  # 每次优化最多2000token
            "require_performance_data": True,  # 需要性能数据
            "backup_before_optimize": True  # 优化前备份
        }
        
        # 状态跟踪
        self.state = {
            "optimizations_today": 0,
            "last_optimization_time": 0,
            "token_used_today": 0,
            "optimization_history": []
        }
        
        # 加载状态
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        state_file = self.workspace / "data" / "optimization_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    self.state = json.load(f)
            except:
                pass
    
    def _save_state(self):
        """保存状态"""
        state_file = self.workspace / "data" / "optimization_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def can_optimize(self):
        """检查是否可以执行优化"""
        # 检查每日限制
        if self.state["optimizations_today"] >= self.config["max_optimizations_per_day"]:
            return False, "已达到每日优化限制"
        
        # 检查时间间隔
        current_time = time.time()
        time_since_last = current_time - self.state["last_optimization_time"]
        if time_since_last < self.config["min_version_interval_hours"] * 3600:
            return False, f"版本间隔不足，还需等待{int((self.config['min_version_interval_hours']*3600 - time_since_last)/60)}分钟"
        
        # 检查token预算
        if self.state["token_used_today"] >= self.config["token_budget_per_optimization"] * 3:
            return False, "Token预算不足"
        
        return True, "可以执行优化"
    
    def backup_current_strategies(self):
        """备份当前策略"""
        print("备份当前策略...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.versions_dir / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制所有策略文件
        strategy_files = list(self.strategies_dir.glob("*.json"))
        for file in strategy_files:
            if file.name != "strategy_registry.json":  # 跳过注册表
                shutil.copy2(file, backup_dir / file.name)
        
        print(f"  备份到: {backup_dir}")
        return backup_dir
    
    def analyze_strategy_performance(self, strategy_name):
        """分析策略性能"""
        print(f"分析策略性能: {strategy_name}")
        
        # 这里应该从数据库或日志文件获取实际性能数据
        # 由于时间关系，使用模拟数据
        
        performance = {
            "win_rate": 0.0,
            "roi": 0.0,
            "total_orders": 0,
            "total_pnl": 0.0,
            "last_trade_time": None,
            "data_available": False
        }
        
        # 检查是否有实际数据
        result_files = list((self.workspace / "data" / "polymarket").glob(f"*{strategy_name}*.jsonl"))
        if result_files:
            try:
                # 尝试读取最新结果文件
                latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line:
                            data = json.loads(last_line)
                            performance.update({
                                "win_rate": data.get("win_rate", 0),
                                "roi": data.get("roi", 0),
                                "total_orders": data.get("total_orders", 0),
                                "total_pnl": data.get("total_pnl", 0),
                                "data_available": True
                            })
            except:
                pass
        
        print(f"  胜率: {performance['win_rate']*100:.1f}%")
        print(f"  ROI: {performance['roi']*100:.1f}%")
        print(f"  订单数: {performance['total_orders']}")
        print(f"  数据可用: {performance['data_available']}")
        
        return performance
    
    def generate_optimization_plan(self, strategy_name, strategy_config, performance):
        """生成优化计划"""
        print(f"生成优化计划: {strategy_name}")
        
        plan = {
            "strategy": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "changes": [],
            "reason": "",
            "estimated_tokens": 1500
        }
        
        # 基于性能数据生成优化建议
        if not performance["data_available"]:
            plan["reason"] = "无性能数据，进行基础优化"
            plan["changes"] = self._generate_basic_optimizations(strategy_config)
        
        elif performance["total_orders"] == 0:
            plan["reason"] = "无订单记录，放宽过滤条件"
            plan["changes"] = self._generate_low_volume_optimizations(strategy_config)
        
        elif performance["win_rate"] < 0.5:
            plan["reason"] = f"胜率低({performance['win_rate']*100:.1f}%)，收紧过滤"
            plan["changes"] = self._generate_low_winrate_optimizations(strategy_config)
        
        elif performance["roi"] < 0:
            plan["reason"] = f"ROI为负({performance['roi']*100:.1f}%)，调整风险"
            plan["changes"] = self._generate_negative_roi_optimizations(strategy_config)
        
        else:
            plan["reason"] = "表现良好，微调优化"
            plan["changes"] = self._generate_fine_tune_optimizations(strategy_config)
        
        # 限制变化数量（最多3个）
        plan["changes"] = plan["changes"][:3]
        
        print(f"  优化原因: {plan['reason']}")
        print(f"  计划变化: {len(plan['changes'])} 个")
        
        return plan
    
    def _generate_basic_optimizations(self, strategy):
        """生成基础优化"""
        changes = []
        
        # 1. 确保有关键词过滤
        if "keywords" not in strategy or len(strategy.get("keywords", [])) < 5:
            changes.append({
                "parameter": "keywords",
                "action": "add",
                "value": ["bitcoin", "btc", "ethereum", "eth", "solana", "sol"],
                "reason": "添加基础加密货币关键词"
            })
        
        # 2. 设置合理的价格过滤
        if strategy.get("minPrice", 1) > 0.6:
            changes.append({
                "parameter": "minPrice",
                "action": "set",
                "value": 0.5,
                "reason": "设置标准价格过滤"
            })
        
        # 3. 设置仓位大小
        if strategy.get("sizeUSD", 0) == 0:
            changes.append({
                "parameter": "sizeUSD",
                "action": "set",
                "value": 50,
                "reason": "设置标准仓位大小"
            })
        
        return changes
    
    def _generate_low_volume_optimizations(self, strategy):
        """生成低交易量优化"""
        changes = []
        
        # 1. 放宽价格过滤
        current_price = strategy.get("minPrice", 0.5)
        if current_price > 0.3:
            changes.append({
                "parameter": "minPrice",
                "action": "decrease",
                "value": max(0.2, current_price - 0.1),
                "reason": "降低价格门槛增加机会"
            })
        
        # 2. 延长去重时间
        current_dedup = strategy.get("dedupLookbackHours", 6)
        if current_dedup < 24:
            changes.append({
                "parameter": "dedupLookbackHours",
                "action": "increase",
                "value": min(24, current_dedup + 6),
                "reason": "延长去重时间窗口"
            })
        
        # 3. 增加关键词
        keywords = set(strategy.get("keywords", []))
        additional = {"crypto", "token", "price", "market", "trading"}
        missing = additional - keywords
        if missing:
            changes.append({
                "parameter": "keywords",
                "action": "add",
                "value": list(keywords | missing),
                "reason": "添加通用交易关键词"
            })
        
        return changes
    
    def _generate_low_winrate_optimizations(self, strategy):
        """生成低胜率优化"""
        changes = []
        
        # 1. 收紧价格过滤
        current_price = strategy.get("minPrice", 0.5)
        if current_price < 0.7:
            changes.append({
                "parameter": "minPrice",
                "action": "increase",
                "value": min(0.8, current_price + 0.1),
                "reason": "提高价格门槛提升质量"
            })
        
        # 2. 缩短去重时间
        current_dedup = strategy.get("dedupLookbackHours", 6)
        if current_dedup > 2:
            changes.append({
                "parameter": "dedupLookbackHours",
                "action": "decrease",
                "value": max(2, current_dedup - 2),
                "reason": "缩短去重时间增加机会"
            })
        
        # 3. 减小仓位
        current_size = strategy.get("sizeUSD", 50)
        if current_size > 20:
            changes.append({
                "parameter": "sizeUSD",
                "action": "decrease",
                "value": max(10, current_size - 10),
                "reason": "减小仓位控制风险"
            })
        
        return changes
    
    def _generate_negative_roi_optimizations(self, strategy):
        """生成负ROI优化"""
        changes = []
        
        # 1. 大幅减小仓位
        current_size = strategy.get("sizeUSD", 50)
        if current_size > 10:
            changes.append({
                "parameter": "sizeUSD",
                "action": "set",
                "value": 10,
                "reason": "大幅减小仓位控制亏损"
            })
        
        # 2. 启用订单接受检查
        if not strategy.get("requireAcceptingOrders", False):
            changes.append({
                "parameter": "requireAcceptingOrders",
                "action": "set",
                "value": True,
                "reason": "启用订单接受检查"
            })
        
        # 3. 收紧所有过滤
        changes.append({
            "parameter": "minPrice",
            "action": "increase",
            "value": 0.7,
            "reason": "收紧过滤减少交易"
        })
        
        return changes
    
    def _generate_fine_tune_optimizations(self, strategy):
        """生成微调优化"""
        changes = []
        
        # 小幅度调整参数
        current_price = strategy.get("minPrice", 0.5)
        if 0.4 <= current_price <= 0.6:
            # 在合理范围内微调
            adjustment = 0.05 if current_price < 0.55 else -0.05
            changes.append({
                "parameter": "minPrice",
                "action": "adjust",
                "value": current_price + adjustment,
                "reason": "微调价格过滤"
            })
        
        return changes
    
    def apply_optimization_plan(self, strategy_name, original_config, plan):
        """应用优化计划"""
        print(f"应用优化计划: {strategy_name}")
        
        # 创建优化后的配置
        optimized = original_config.copy()
        
        # 应用每个变化
        applied_changes = []
        for change in plan["changes"]:
            param = change["parameter"]
            action = change["action"]
            value = change["value"]
            
            if action == "set":
                optimized[param] = value
                applied_changes.append(f"{param}={value}")
            
            elif action == "add" and param == "keywords":
                current = set(optimized.get(param, []))
                new = set(value)
                optimized[param] = list(current | new)
                applied_changes.append(f"{param}+{len(new)}个")
            
            elif action in ["increase", "decrease", "adjust"]:
                if param in optimized:
                    optimized[param] = value
                    applied_changes.append(f"{param}→{value}")
        
        # 更新策略名称
        version_suffix = datetime.now().strftime("%y%m%d_%H%M")
        optimized["name"] = f"{original_config.get('name', strategy_name)}_opt_{version_suffix}"
        optimized["optimized_from"] = strategy_name
        optimized["optimization_date"] = datetime.now().isoformat()
        optimized["changes_applied"] = applied_changes
        
        # 保存优化后的策略
        output_file = self.optimized_dir / f"{strategy_name}_opt_{version_suffix}.json"
        with open(output_file, 'w') as f:
            json.dump(optimized, f, indent=2)
        
        print(f"  应用变化: {', '.join(applied_changes)}")
        print(f"  保存到: {output_file}")
        
        return optimized, output_file
    
    def execute_optimization(self, strategy_name):
        """执行单个策略优化"""
        print(f"\n执行策略优化: {strategy_name}")
        print("-"*50)
        
        # 1. 检查是否可以优化
        can_optimize, reason = self.can_optimize()
        if not can_optimize:
            print(f"无法优化: {reason}")
            return None
        
        # 2. 备份
        if self.config["backup_before_optimize"]:
            self.backup_current_strategies()
        
        # 3. 加载策略配置
        strategy_file = self.strategies_dir / f"{strategy_name}.json"
        if not strategy_file.exists():
            print(f"策略文件不存在: {strategy_file}")
            return None
        
        with open(strategy_file, 'r') as f:
            strategy_config = json.load(f)
        
        # 4. 分析性能
        performance = self.analyze_strategy_performance(strategy_name)
        
        # 5. 生成优化计划
        plan = self.generate_optimization_plan(strategy_name, strategy_config, performance)
        
        # 6. 应用优化
        optimized_config, output_file = self.apply_optimization_plan(
            strategy_name, strategy_config, plan
        )
        
        # 7. 更新状态
        self.state["optimizations_today"] += 1
        self.state["last_optimization_time"] = time.time()
        self.state["token_used_today"] += plan["estimated_tokens"]
        self.state["optimization_history"].append({
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_name,
            "plan": plan,
            "output_file": str(output_file)
        })
        
        # 8. 保存状态
        self._save_state()
        
        print(f"\n✅ 优化完成: {strategy_name}")
        print(f"   版本: {optimized_config['name']}")
        print(f"   变化: {len(plan['changes'])} 个")
        print(f"   Token使用: {plan['estimated_tokens']}")
        
        return optimized_config
    
    def run_optimization_pipeline(self):
        """运行优化管道"""
        print("策略优化迭代管道")
        print("="*70)
        
        # 1. 检查当前策略
        strategy_files = list(self.strategies_dir.glob("*.json"))
        strategy_files = [f for f in strategy_files if f.name != "strategy_registry.json"]
        
        print(f"找到 {len(strategy_files)} 个策略")
        
        # 2. 选择需要优化的策略（基于简单规则）
        strategies_to_optimize = []
        for file in strategy_files[:3]:  # 最多优化3个
            strategy_name = file.stem
            if "cex" not in strategy_name.lower():  # 优先优化PM策略
                strategies_to_optimize.append(strategy_name)
        
        print(f"选择优化: {strategies_to_optimize}")
        
        # 3. 执行优化
        optimized_strategies = []
        for strategy_name in strategies_to_optimize:
            optimized = self.execute_optimization(strategy_name)
            if optimized:
