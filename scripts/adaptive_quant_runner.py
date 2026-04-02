#!/usr/bin/env python3
"""
自适应量化运行器
集成策略版本管理、自适应优化、执行监控的统一运行器
"""

import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy_version_manager import StrategyVersionManager
from adaptive_optimizer import AdaptiveOptimizer, ProblemType
from execution_monitor import ExecutionMonitor

class AdaptiveQuantRunner:
    """自适应量化运行器"""
    
    def __init__(self):
        print("🚀 初始化自适应量化运行器")
        print("="*60)
        
        # 初始化组件
        self.version_manager = StrategyVersionManager()
        self.optimizer = AdaptiveOptimizer(self.version_manager)
        self.execution_monitor = ExecutionMonitor()
        
        # 配置
        self.config = {
            "optimization_interval_hours": 24,  # 每24小时运行一次优化
            "min_sample_size": 50,  # 最小样本量
            "target_roi_threshold": 0.01,  # 目标ROI阈值
            "max_optimization_iterations": 5,  # 最大优化迭代次数
            "execution_gate_enabled": True,  # 启用执行闸门
            "drift_threshold_bps": 50,  # 价格漂移阈值
            "signal_ttl_seconds": 30  # 信号生存时间
        }
        
        # 状态
        self.last_optimization_time = {}
        self.running_strategies = []
    
    def register_strategy(self, strategy_id: str, strategy_type: str, 
                         initial_params: Dict, description: str = ""):
        """注册新策略"""
        print(f"\n📝 注册策略: {strategy_id}")
        
        # 注册到版本管理器
        self.version_manager.register_strategy(strategy_id, strategy_type, description)
        
        # 创建初始版本
        version_name = self.version_manager.create_version(
            strategy_id=strategy_id,
            params=initial_params,
            hypothesis=f"初始版本: {description}"
        )
        
        # 初始化指标
        self.version_manager.update_metrics(version_name, {
            "sample_n": 0,
            "win_rate": 0.0,
            "roi_after_cost": 0.0,
            "drawdown_proxy": 0.0,
            "orders_per_day": 0.0,
            "trades_per_day": 0.0
        })
        
        # 添加到运行列表
        self.running_strategies.append(strategy_id)
        
        print(f"✅ 策略注册完成")
        print(f"   初始版本: {version_name}")
        print(f"   初始参数: {json.dumps(initial_params, indent=2)}")
        
        return version_name
    
    def run_strategy_cycle(self, strategy_id: str):
        """运行策略周期"""
        print(f"\n🔄 运行策略周期: {strategy_id}")
        print("-"*40)
        
        # 获取当前最佳版本
        current_version = self.version_manager.get_best_version(strategy_id)
        if not current_version:
            print(f"❌ 策略 {strategy_id} 无可用版本")
            return False
        
        # 获取版本数据
        data = self.version_manager.load_db()
        version_data = data["versions"][current_version]
        params = version_data["changed_params"]
        
        print(f"当前版本: {current_version}")
        print(f"当前参数: {json.dumps(params, indent=2)}")
        
        # 运行策略（这里需要调用实际策略代码）
        # 暂时使用模拟运行
        execution_results = self._simulate_strategy_run(strategy_id, current_version, params)
        
        # 记录执行
        for result in execution_results:
            exec_id = self.execution_monitor.record_execution(
                strategy_id=strategy_id,
                version=current_version,
                signal_data=result["signal_data"],
                execution_data=result["execution_data"]
            )
            
            # 检查执行闸门（模拟）
            if self.config["execution_gate_enabled"]:
                passed, reason = self.execution_monitor.check_execution_gate(
                    strategy_id=strategy_id,
                    signal_data=result["signal_data"],
                    current_market_data=result.get("market_data", {})
                )
                
                if not passed:
                    print(f"🚫 执行被闸门拒绝: {reason}")
        
        # 更新策略指标
        new_metrics = self._calculate_strategy_metrics(strategy_id)
        self.version_manager.update_metrics(current_version, new_metrics)
        
        print(f"✅ 策略周期完成")
        print(f"   样本量: {new_metrics.get('sample_n', 0)}")
        print(f"   ROI: {new_metrics.get('roi_after_cost', 0):.4f}")
        print(f"   频率: {new_metrics.get('orders_per_day', 0):.1f} 单/天")
        
        return True
    
    def check_and_optimize(self, strategy_id: str):
        """检查并优化策略"""
        print(f"\n🔍 检查优化需求: {strategy_id}")
        
        # 检查优化间隔
        current_time = time.time()
        last_opt = self.last_optimization_time.get(strategy_id, 0)
        hours_since_last = (current_time - last_opt) / 3600
        
        if hours_since_last < self.config["optimization_interval_hours"]:
            print(f"⏳ 距离上次优化仅 {hours_since_last:.1f} 小时，跳过")
            return None
        
        # 获取当前版本和指标
        current_version = self.version_manager.get_best_version(strategy_id)
        if not current_version:
            return None
        
        data = self.version_manager.load_db()
        version_data = data["versions"][current_version]
        metrics = version_data["metrics"]
        
        # 检查是否需要优化
        needs_optimization = self._check_optimization_needed(metrics)
        
        if not needs_optimization:
            print(f"✅ 当前版本表现良好，无需优化")
            self.last_optimization_time[strategy_id] = current_time
            return None
        
        # 运行优化管道
        print(f"🔄 启动优化管道")
        final_version = self.optimizer.run_optimization_pipeline(
            strategy_id=strategy_id,
            max_iterations=self.config["max_optimization_iterations"]
        )
        
        self.last_optimization_time[strategy_id] = current_time
        
        return final_version
    
    def _check_optimization_needed(self, metrics: Dict) -> bool:
        """检查是否需要优化"""
        # 检查样本量
        if metrics.get("sample_n", 0) < self.config["min_sample_size"]:
            return True
        
        # 检查ROI
        if metrics.get("roi_after_cost", 0) < self.config["target_roi_threshold"]:
            return True
        
        # 检查频率
        if metrics.get("orders_per_day", 0) < 10:
            return True
        
        # 检查胜率
        if metrics.get("win_rate", 0) < 0.45:
            return True
        
        return False
    
    def _simulate_strategy_run(self, strategy_id: str, version: str, 
                              params: Dict) -> List[Dict]:
        """模拟策略运行（实际使用时应替换为真实策略）"""
        results = []
        
        # 模拟几次执行
        num_executions = 5  # 模拟5次执行
        
        for i in range(num_executions):
            # 生成信号数据
            signal_price = 50000.0 + (i * 100)  # 模拟价格变化
            signal_time = time.time() - (num_executions - i) * 10  # 模拟不同时间
            
            signal_data = {
                "signal_timestamp": signal_time,
                "decision_timestamp": signal_time + 0.5,
                "signal_price": signal_price,
                "signal_ttl_seconds": self.config["signal_ttl_seconds"],
                "drift_threshold_bps": self.config["drift_threshold_bps"],
                "expected_edge_bps": 25,
                "min_edge_threshold_bps": 10
            }
            
            # 模拟执行数据
            fill_time = signal_time + 1.5 + (i * 0.2)  # 模拟不同填充时间
            fill_price = signal_price * (1 + (random.uniform(-0.001, 0.001)))  # 模拟价格漂移
            
            execution_data = {
                "submit_timestamp": signal_time + 1.0,
                "fill_timestamp": fill_time,
                "confirm_price": signal_price * (1 + random.uniform(-0.0005, 0.0005)),
                "fill_price": fill_price,
                "filled": random.random() > 0.2,  # 80%填充率
                "fee": 0.001,
                "slippage": random.uniform(0.00005, 0.0002)
            }
            
            # 模拟市场数据
            market_data = {
                "price": fill_price,
                "liquidity": random.randint(30000, 70000),
                "volatility": random.randint(100, 200)
            }
            
            results.append({
                "signal_data": signal_data,
                "execution_data": execution_data,
                "market_data": market_data
            })
        
        return results
    
    def _calculate_strategy_metrics(self, strategy_id: str) -> Dict:
        """计算策略指标（基于执行记录）"""
        # 获取最近24小时的执行记录
        report = self.execution_monitor.get_performance_report(strategy_id, lookback_hours=24)
        
        # 计算指标
        metrics = {
            "sample_n": report.get("total_executions", 0),
            "win_rate": 0.55,  # 模拟胜率
            "roi_after_cost": random.uniform(-0.005, 0.02),  # 模拟ROI
            "drawdown_proxy": random.uniform(0.01, 0.03),  # 模拟回撤
            "orders_per_day": report.get("total_executions", 0) / 24,  # 转换为每天
            "trades_per_day": report.get("completed", 0) / 24  # 转换为每天
        }
        
        return metrics
    
    def generate_report(self, strategy_id: str):
        """生成综合报告"""
        print(f"\n📊 综合报告: {strategy_id}")
        print("="*60)
        
        # 版本信息
        current_version = self.version_manager.get_best_version(strategy_id)
        print(f"当前最佳版本: {current_version}")
        
        # 策略树
        self.version_manager.print_strategy_tree(strategy_id)
        
        # 性能报告
        report = self.execution_monitor.get_performance_report(strategy_id, lookback_hours=24)
        
        print(f"\n📈 性能指标 (最近24小时)")
        print(f"总执行: {report.get('total_executions', 0)}")
        print(f"完成率: {report.get('completion_rate', 0):.1%}")
        
        if "latency_stats" in report:
            latency = report["latency_stats"]
            print(f"平均延迟: {latency.get('avg_ms', 0):.1f}ms")
            print(f"P95延迟: {latency.get('p95_ms', 0):.1f}ms")
        
        if "drift_stats" in report:
            drift = report["drift_stats"]
            print(f"平均漂移: {drift.get('avg_bps', 0):.1f}bps")
            print(f"最大漂移: {drift.get('max_bps', 0):.1f}bps")
        
        # 拒绝分析
        if report.get("rejection_analysis"):
            print(f"\n🚫 拒绝分析")
            for reason, count in report["rejection_analysis"].items():
                print(f"  {reason}: {count}次")
        
        # 优化历史
        print(f"\n🔄 优化历史")
        self.optimizer.print_optimization_history()
        
        # 最近执行记录
        self.execution_monitor.print_recent_executions(strategy_id, limit=5)
    
    def run_continuous_cycle(self, interval_minutes: int = 60):
        """运行连续周期"""
        print(f"\n⏱️ 启动连续运行周期 (间隔: {interval_minutes}分钟)")
        print("="*60)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n🌀 周期 #{cycle_count} - {datetime.utcnow().isoformat()}")
                print("-"*40)
                
                # 运行每个策略
                for strategy_id in self.running_strategies:
                    print(f"\n处理策略: {strategy_id}")
                    
                    # 1. 运行策略周期
                    self.run_strategy_cycle(strategy_id)
                    
                    # 2. 检查并优化
                    self.check_and_optimize(strategy_id)
                    
                    # 3. 生成报告（每3个周期一次）
                    if cycle_count % 3 == 0:
                        self.generate_report(strategy_id)
                
                print(f"\n✅ 周期 #{cycle_count} 完成")
                print(f"等待 {interval_minutes} 分钟...")
                
                # 等待下一个周期
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n🛑 用户中断")
            print(f"总运行周期: {cycle_count}")
            
            # 生成最终报告
            for strategy_id in self.running_strategies:
                self.generate_report(strategy_id)

# 使用示例
if __name__ == "__main__":
    
    # 初始化运行器
    runner = AdaptiveQuantRunner()
    
    # 注册策略
    cex_params = {
        "window": 5,
        "threshold": 0.005,  # 0.5%
        "max_position": 0.1,
        "stop_loss": 0.02,
        "take_profit": 0.04
    }
    
    cex_version = runner.register_strategy(
        strategy_id="cex_btc_5m_breakout",
        strategy_type="cex",
        initial_params=cex_params,
        description="BTC 5分钟突破策略"
    )
    
    pm_params = {
        "min_probability": 0.6,
        "max_days_to_resolve": 7,
        "min_liquidity": 1000,
        "max_position": 0.05
    }
    
    pm_version = runner.register_strategy(
        strategy_id="pm_br_v2_relaxed",
        strategy_type="pm",
        initial_params=pm_params,
        description="PM BR宽松版策略"
    )
    
    # 运行几个周期
    print(f"\n🏃 运行演示周期...")
    
    for i in range(3):
        print(f"\n周期 {i+1}/3")
        print("-"*40)
        
        # 运行CEX策略
        runner.run_strategy_cycle("cex_btc_5m_breakout")
        
        # 运行PM策略
        runner.run_strategy_cycle("pm_br_v2_relaxed")
        
        # 每2个周期检查一次优化
        if (i + 1) % 2 == 0:
            runner.check_and_optimize("cex_btc_5m_breakout")
            runner.check_and_optimize("pm_br_v2_relaxed")
    
    # 生成最终报告
    print(f"\n📋 最终报告")
    print("="*60)
    
    runner.generate_report("cex_btc_5m_breakout")
    runner.generate_report("pm_br_v2_relaxed")
    
    print(f"\n✅ 自适应量化运行器演示完成")
    print(f"\n下一步:")
    print(f"1. 将实际策略代码集成到运行器中")
    print(f"2. 配置真实数据源")
    print(f"3. 设置定时运行")
    print(f"4. 监控和调整参数")