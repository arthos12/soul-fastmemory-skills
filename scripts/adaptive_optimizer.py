#!/usr/bin/env python3
"""
自适应优化器
实现自适应量化软件的优化闭环
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import random

class ProblemType(Enum):
    """问题类型枚举"""
    SAMPLE_INSUFFICIENT = "sample_insufficient"  # 样本不足
    FREQUENCY_INSUFFICIENT = "frequency_insufficient"  # 下单频率不足
    WIN_RATE_LOW = "win_rate_low"  # 胜率不足
    RISK_REWARD_POOR = "risk_reward_poor"  # 盈亏比不足
    COST_SLIPPAGE_HIGH = "cost_slippage_high"  # 手续费/滑点吞噬
    MARKET_SUPPLY_LOW = "market_supply_low"  # 盘口/市场供给不足
    BACKTEST_ERROR = "backtest_error"  # 回填口径错误
    STRATEGY_DRIFT = "strategy_drift"  # 策略漂移/版本污染

class AdaptiveOptimizer:
    """自适应优化器"""
    
    def __init__(self, version_manager):
        self.version_manager = version_manager
        self.optimization_history = []
    
    def diagnose_problem(self, strategy_id: str, version_name: str, 
                        metrics: Dict) -> List[ProblemType]:
        """诊断问题类型"""
        problems = []
        
        # 获取版本数据
        data = self.version_manager.load_db()
        if version_name not in data["versions"]:
            return problems
        
        version_data = data["versions"][version_name]
        version_metrics = version_data["metrics"]
        
        # 1. 检查样本不足
        if version_metrics.get("sample_n", 0) < 50:
            problems.append(ProblemType.SAMPLE_INSUFFICIENT)
        
        # 2. 检查下单频率不足
        orders_per_day = version_metrics.get("orders_per_day", 0)
        if orders_per_day < 10:  # 每天少于10单
            problems.append(ProblemType.FREQUENCY_INSUFFICIENT)
        
        # 3. 检查胜率不足
        win_rate = version_metrics.get("win_rate", 0)
        if win_rate < 0.45:  # 胜率低于45%
            problems.append(ProblemType.WIN_RATE_LOW)
        
        # 4. 检查盈亏比不足（通过ROI判断）
        roi = version_metrics.get("roi_after_cost", 0)
        if roi < 0.001:  # ROI低于0.1%
            problems.append(ProblemType.RISK_REWARD_POOR)
        
        # 5. 检查手续费/滑点（通过比较理论收益和实际收益）
        # 这里简化处理，如果有成本字段可以更精确
        
        # 6. 检查市场供给（通过订单生成率）
        # 需要策略提供更多上下文信息
        
        return problems
    
    def generate_minimal_modification(self, strategy_id: str, version_name: str,
                                    problems: List[ProblemType]) -> Dict:
        """生成最小修改版本"""
        # 获取当前版本参数
        data = self.version_manager.load_db()
        if version_name not in data["versions"]:
            return {}
        
        current_params = data["versions"][version_name]["changed_params"]
        new_params = current_params.copy()
        
        # 根据问题类型调整参数
        modifications = []
        
        for problem in problems:
            if problem == ProblemType.SAMPLE_INSUFFICIENT:
                # 增加样本：降低门槛或扩大窗口
                if "threshold" in new_params:
                    new_params["threshold"] = new_params["threshold"] * 0.8  # 降低20%
                    modifications.append("降低阈值以增加样本")
            
            elif problem == ProblemType.FREQUENCY_INSUFFICIENT:
                # 提高频率：降低门槛或缩短窗口
                if "threshold" in new_params:
                    new_params["threshold"] = new_params["threshold"] * 0.7  # 降低30%
                    modifications.append("降低阈值以提高频率")
                if "window" in new_params and new_params["window"] > 3:
                    new_params["window"] = max(3, new_params["window"] - 2)  # 缩短窗口
                    modifications.append("缩短时间窗口以提高频率")
            
            elif problem == ProblemType.WIN_RATE_LOW:
                # 提高胜率：提高门槛
                if "threshold" in new_params:
                    new_params["threshold"] = new_params["threshold"] * 1.3  # 提高30%
                    modifications.append("提高阈值以提高胜率")
            
            elif problem == ProblemType.RISK_REWARD_POOR:
                # 改善盈亏比：调整止损止盈
                if "stop_loss" not in new_params:
                    new_params["stop_loss"] = 0.02  # 添加2%止损
                    modifications.append("添加止损以改善盈亏比")
                if "take_profit" not in new_params:
                    new_params["take_profit"] = 0.04  # 添加4%止盈
                    modifications.append("添加止盈以改善盈亏比")
        
        # 确保只修改1-3个参数
        changed_keys = [k for k in new_params.keys() if new_params[k] != current_params.get(k)]
        if len(changed_keys) > 3:
            # 随机保留3个修改
            keep_keys = random.sample(changed_keys, 3)
            for key in changed_keys:
                if key not in keep_keys:
                    new_params[key] = current_params.get(key)
        
        return {
            "new_params": new_params,
            "modifications": modifications,
            "changed_keys": [k for k in new_params.keys() if new_params[k] != current_params.get(k)]
        }
    
    def create_optimization_cycle(self, strategy_id: str, version_name: str,
                                 metrics: Dict) -> Optional[str]:
        """创建一个优化周期"""
        print(f"\n🔄 开始优化周期: {strategy_id} - {version_name}")
        print("="*60)
        
        # 1. 诊断问题
        problems = self.diagnose_problem(strategy_id, version_name, metrics)
        print(f"诊断结果: {[p.value for p in problems]}")
        
        if not problems:
            print("✅ 未发现问题，无需优化")
            return None
        
        # 2. 生成最小修改
        modification = self.generate_minimal_modification(strategy_id, version_name, problems)
        if not modification["changed_keys"]:
            print("❌ 无法生成有效修改")
            return None
        
        print(f"修改方案: {modification['modifications']}")
        print(f"参数变化: {modification['changed_keys']}")
        
        # 3. 创建新版本
        hypothesis = f"优化: {', '.join(modification['modifications'])}"
        new_version = self.version_manager.create_version(
            strategy_id=strategy_id,
            params=modification["new_params"],
            parent_version=version_name,
            hypothesis=hypothesis
        )
        
        # 4. 记录优化历史
        optimization_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_id": strategy_id,
            "from_version": version_name,
            "to_version": new_version,
            "problems": [p.value for p in problems],
            "modifications": modification["modifications"],
            "changed_params": modification["changed_keys"]
        }
        self.optimization_history.append(optimization_record)
        
        print(f"✅ 创建优化版本: {new_version}")
        return new_version
    
    def compare_and_decide(self, old_version: str, new_version: str,
                          improvement_threshold: float = 0.01) -> Tuple[bool, Dict]:
        """比较版本并决定是否保留"""
        print(f"\n📊 版本比较: {old_version} vs {new_version}")
        print("="*60)
        
        # 获取版本数据
        data = self.version_manager.load_db()
        if old_version not in data["versions"] or new_version not in data["versions"]:
            print("❌ 版本不存在")
            return False, {}
        
        old_data = data["versions"][old_version]
        new_data = data["versions"][new_version]
        
        # 比较关键指标
        comparison = {
            "roi_improvement": new_data["metrics"]["roi_after_cost"] - old_data["metrics"]["roi_after_cost"],
            "win_rate_improvement": new_data["metrics"]["win_rate"] - old_data["metrics"]["win_rate"],
            "frequency_improvement": new_data["metrics"]["orders_per_day"] - old_data["metrics"]["orders_per_day"],
            "sample_size_adequate": new_data["metrics"]["sample_n"] >= 50
        }
        
        print(f"ROI改进: {comparison['roi_improvement']:.4f}")
        print(f"胜率改进: {comparison['win_rate_improvement']:.4f}")
        print(f"频率改进: {comparison['frequency_improvement']:.2f} 单/天")
        print(f"样本充足: {comparison['sample_size_adequate']}")
        
        # 决定是否保留新版本
        should_promote = (
            comparison["roi_improvement"] > improvement_threshold or  # ROI显著改善
            (comparison["win_rate_improvement"] > 0.05 and comparison["sample_size_adequate"]) or  # 胜率显著改善
            (comparison["frequency_improvement"] > 5 and old_data["metrics"]["orders_per_day"] < 10)  # 频率显著改善且原频率低
        )
        
        if should_promote:
            print("✅ 新版本表现更好，准备提升")
            self.version_manager.promote_version(new_version)
        else:
            print("❌ 新版本未改善，标记为拒绝")
            self.version_manager.reject_version(new_version, "未达到改进阈值")
        
        return should_promote, comparison
    
    def run_optimization_pipeline(self, strategy_id: str, max_iterations: int = 5):
        """运行优化管道"""
        print(f"\n🚀 启动优化管道: {strategy_id}")
        print("="*60)
        
        # 获取当前最佳版本
        current_version = self.version_manager.get_best_version(strategy_id)
        if not current_version:
            print(f"❌ 策略 {strategy_id} 无可用版本")
            return
        
        iterations = 0
        improvements = 0
        
        while iterations < max_iterations:
            iterations += 1
            print(f"\n迭代 {iterations}/{max_iterations}")
            print("-"*40)
            
            # 获取当前版本指标
            data = self.version_manager.load_db()
            if current_version not in data["versions"]:
                break
            
            current_metrics = data["versions"][current_version]["metrics"]
            
            # 运行优化周期
            new_version = self.create_optimization_cycle(
                strategy_id, current_version, current_metrics
            )
            
            if not new_version:
                print("⏹️ 优化周期结束")
                break
            
            # 模拟测试新版本（这里需要实际运行策略）
            # 暂时使用模拟数据
            simulated_metrics = self.simulate_test_results(new_version)
            self.version_manager.update_metrics(new_version, simulated_metrics)
            
            # 比较并决定
            improved, comparison = self.compare_and_decide(current_version, new_version)
            
            if improved:
                improvements += 1
                current_version = new_version
                print(f"✅ 采纳新版本: {new_version}")
            else:
                print(f"❌ 保留原版本: {current_version}")
            
            # 检查是否连续无改进
            if iterations - improvements > 2:
                print("⚠️ 连续多次无改进，停止优化")
                break
        
        print(f"\n🎯 优化管道完成")
        print(f"总迭代: {iterations}")
        print(f"成功改进: {improvements}")
        print(f"最终版本: {current_version}")
        
        return current_version
    
    def simulate_test_results(self, version_name: str) -> Dict:
        """模拟测试结果（实际使用时应替换为真实策略测试）"""
        # 这里模拟策略测试结果
        # 实际实现应该运行策略并收集真实指标
        
        return {
            "sample_n": random.randint(80, 150),
            "win_rate": random.uniform(0.45, 0.65),
            "roi_after_cost": random.uniform(-0.01, 0.03),
            "drawdown_proxy": random.uniform(0.01, 0.05),
            "orders_per_day": random.uniform(15, 40),
            "trades_per_day": random.uniform(10, 30)
        }
    
    def print_optimization_history(self):
        """打印优化历史"""
        print("\n📜 优化历史")
        print("="*60)
        
        for i, record in enumerate(self.optimization_history[-10:], 1):  # 显示最近10条
            print(f"{i}. {record['timestamp']}")
            print(f"   策略: {record['strategy_id']}")
            print(f"   从: {record['from_version']}")
            print(f"   到: {record['to_version']}")
            print(f"   问题: {record['problems']}")
            print(f"   修改: {record['modifications']}")
            print()

# 使用示例
if __name__ == "__main__":
    from strategy_version_manager import StrategyVersionManager
    
    # 初始化
    version_manager = StrategyVersionManager()
    optimizer = AdaptiveOptimizer(version_manager)
    
    # 确保策略已注册
    version_manager.register_strategy("cex_btc_5m_breakout", "cex", "BTC 5分钟突破策略")
    
    # 运行优化管道
    final_version = optimizer.run_optimization_pipeline("cex_btc_5m_breakout", max_iterations=3)
    
    # 打印优化历史
    optimizer.print_optimization_history()
    
    # 打印最终策略树
    version_manager.print_strategy_tree("cex_btc_5m_breakout")
    
    print("\n✅ 自适应优化器演示完成")