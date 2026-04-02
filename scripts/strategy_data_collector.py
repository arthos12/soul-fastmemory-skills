#!/usr/bin/env python3
"""
策略数据收集器
收集现有策略的运行数据，为优化提供依据
严格控制token使用，避免不必要的LLM调用
"""

import os
import json
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path
import statistics

class StrategyDataCollector:
    """策略数据收集器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.data_dir = self.workspace / "data"
        self.strategies_dir = self.workspace / "strategies"
        
        # Token使用控制
        self.token_usage = {
            "today": 0,
            "daily_limit": 50000,  # 每日5万token上限
            "operations": []
        }
    
    def collect_all_strategy_data(self, days_back=7):
        """收集所有策略数据"""
        print("开始收集策略数据...")
        print("="*70)
        
        all_data = {}
        
        # 1. 收集PM策略数据
        pm_data = self.collect_pm_strategy_data(days_back)
        all_data["pm_strategies"] = pm_data
        
        # 2. 收集CEX策略数据
        cex_data = self.collect_cex_strategy_data(days_back)
        all_data["cex_strategies"] = cex_data
        
        # 3. 收集策略配置文件
        config_data = self.collect_strategy_configs()
        all_data["configs"] = config_data
        
        # 4. 分析性能趋势
        performance_trends = self.analyze_performance_trends(all_data)
        all_data["trends"] = performance_trends
        
        # 5. 保存数据
        self.save_collected_data(all_data)
        
        # 6. 打印摘要
        self.print_summary(all_data)
        
        return all_data
    
    def collect_pm_strategy_data(self, days_back):
        """收集PM策略数据"""
        print("收集PM策略数据...")
        
        pm_data = {}
        pm_dir = self.data_dir / "polymarket"
        
        if not pm_dir.exists():
            print("  PM数据目录不存在")
            return pm_data
        
        # 查找策略结果文件
        result_files = list(pm_dir.glob("paper_results_*.jsonl"))
        print(f"  找到 {len(result_files)} 个结果文件")
        
        # 按策略分组
        strategy_results = {}
        for file in result_files[:50]:  # 限制数量
            strategy_name = self._extract_strategy_name(file.name)
            if strategy_name not in strategy_results:
                strategy_results[strategy_name] = []
            
            try:
                with open(file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        # 取最后一行（最新结果）
                        last_line = lines[-1].strip()
                        if last_line:
                            data = json.loads(last_line)
                            strategy_results[strategy_name].append(data)
            except:
                continue
        
        # 分析每个策略
        for strategy, results in strategy_results.items():
            if results:
                analysis = self._analyze_strategy_results(results)
                pm_data[strategy] = analysis
                print(f"  {strategy}: {len(results)} 个结果，胜率: {analysis.get('win_rate', 0)*100:.1f}%")
        
        return pm_data
    
    def collect_cex_strategy_data(self, days_back):
        """收集CEX策略数据"""
        print("收集CEX策略数据...")
        
        cex_data = {}
        cex_dir = self.data_dir / "cex"
        
        if not cex_dir.exists():
            print("  CEX数据目录不存在")
            return cex_data
        
        # 查找交易记录文件
        trade_files = list(cex_dir.glob("*.jsonl"))
        print(f"  找到 {len(trade_files)} 个交易文件")
        
        # 这里可以添加CEX数据分析逻辑
        # 由于时间关系，先返回基础数据
        
        return cex_data
    
    def collect_strategy_configs(self):
        """收集策略配置文件"""
        print("收集策略配置...")
        
        configs = {}
        strategy_files = list(self.strategies_dir.glob("*.json"))
        
        for file in strategy_files:
            try:
                with open(file, 'r') as f:
                    config = json.load(f)
                    configs[file.stem] = {
                        "name": config.get("name", file.stem),
                        "params": {k: v for k, v in config.items() if k != "name"},
                        "file_size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    }
            except:
                continue
        
        print(f"  收集到 {len(configs)} 个策略配置")
        return configs
    
    def _extract_strategy_name(self, filename):
        """从文件名提取策略名称"""
        # 移除前缀和后缀
        name = filename.replace("paper_results_", "").replace(".jsonl", "")
        
        # 提取策略部分
        if "_" in name:
            # 尝试提取日期前的部分
            parts = name.split("_")
            for i, part in enumerate(parts):
                if part.isdigit() and len(part) == 8:  # 类似20260317
                    return "_".join(parts[:i])
        
        return name
    
    def _analyze_strategy_results(self, results):
        """分析策略结果"""
        if not results:
            return {}
        
        # 使用最新结果
        latest = results[-1]
        
        analysis = {
            "total_orders": latest.get("total_orders", 0),
            "win_orders": latest.get("win_orders", 0),
            "lose_orders": latest.get("lose_orders", 0),
            "total_pnl": latest.get("total_pnl", 0),
            "win_rate": latest.get("win_rate", 0),
            "roi": latest.get("roi", 0),
            "timestamp": latest.get("timestamp", ""),
            "sample_size": len(results)
        }
        
        # 如果有多个结果，计算趋势
        if len(results) > 1:
            win_rates = [r.get("win_rate", 0) for r in results]
            pnls = [r.get("total_pnl", 0) for r in results]
            
            analysis["trend"] = {
                "win_rate_trend": "上升" if win_rates[-1] > win_rates[0] else "下降",
                "pnl_trend": "上升" if pnls[-1] > pnls[0] else "下降",
                "stability": statistics.stdev(win_rates) if len(win_rates) > 1 else 0
            }
        
        return analysis
    
    def analyze_performance_trends(self, all_data):
        """分析性能趋势"""
        print("分析性能趋势...")
        
        trends = {
            "overall": {},
            "by_strategy": {},
            "recommendations": []
        }
        
        # 分析PM策略
        pm_strategies = all_data.get("pm_strategies", {})
        if pm_strategies:
            # 计算总体表现
            win_rates = [s.get("win_rate", 0) for s in pm_strategies.values()]
            rois = [s.get("roi", 0) for s in pm_strategies.values()]
            
            if win_rates:
                trends["overall"]["avg_win_rate"] = statistics.mean(win_rates)
                trends["overall"]["max_win_rate"] = max(win_rates)
                trends["overall"]["min_win_rate"] = min(win_rates)
            
            if rois:
                trends["overall"]["avg_roi"] = statistics.mean(rois)
                trends["overall"]["max_roi"] = max(rois)
                trends["overall"]["min_roi"] = min(rois)
            
            # 按策略分析
            for name, data in pm_strategies.items():
                strategy_trend = {
                    "win_rate": data.get("win_rate", 0),
                    "roi": data.get("roi", 0),
                    "orders": data.get("total_orders", 0),
                    "status": self._assess_strategy_status(data)
                }
                trends["by_strategy"][name] = strategy_trend
                
                # 生成建议
                recommendation = self._generate_recommendation(name, data)
                if recommendation:
                    trends["recommendations"].append(recommendation)
        
        return trends
    
    def _assess_strategy_status(self, data):
        """评估策略状态"""
        win_rate = data.get("win_rate", 0)
        roi = data.get("roi", 0)
        orders = data.get("total_orders", 0)
        
        if orders == 0:
            return "无数据"
        elif win_rate > 0.6 and roi > 0.1:
            return "优秀"
        elif win_rate > 0.5 and roi > 0:
            return "良好"
        elif win_rate > 0.4:
            return "一般"
        else:
            return "需要优化"
    
    def _generate_recommendation(self, strategy_name, data):
        """生成优化建议"""
        win_rate = data.get("win_rate", 0)
        roi = data.get("roi", 0)
        orders = data.get("total_orders", 0)
        
        if orders == 0:
            return None
        
        recommendation = {
            "strategy": strategy_name,
            "priority": "低",
            "action": "保持",
            "reason": ""
        }
        
        if win_rate < 0.4:
            recommendation["priority"] = "高"
            recommendation["action"] = "收紧过滤条件"
            recommendation["reason"] = f"胜率过低: {win_rate*100:.1f}%"
        
        elif roi < 0:
            recommendation["priority"] = "中"
            recommendation["action"] = "调整仓位或止损"
            recommendation["reason"] = f"ROI为负: {roi*100:.1f}%"
        
        elif orders < 10:
            recommendation["priority"] = "中"
            recommendation["action"] = "放宽条件增加机会"
            recommendation["reason"] = f"订单数少: {orders}"
        
        return recommendation
    
    def save_collected_data(self, data):
        """保存收集的数据"""
        output_dir = self.data_dir / "analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"strategy_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"数据已保存到: {output_file}")
    
    def print_summary(self, data):
        """打印数据摘要"""
        print("\n" + "="*70)
        print("策略数据收集完成")
        print("="*70)
        
        # PM策略摘要
        pm_strategies = data.get("pm_strategies", {})
        if pm_strategies:
            print("\nPM策略表现:")
            print(f"{'策略':<20} {'订单数':<8} {'胜率':<8} {'ROI':<8} {'状态':<10}")
            print("-"*60)
            
            for name, stats in sorted(pm_strategies.items(), 
                                     key=lambda x: x[1].get("win_rate", 0), 
                                     reverse=True):
                orders = stats.get("total_orders", 0)
                win_rate = stats.get("win_rate", 0) * 100
                roi = stats.get("roi", 0) * 100
                status = self._assess_strategy_status(stats)
                
                print(f"{name:<20} {orders:<8} {win_rate:<7.1f}% {roi:<7.1f}% {status:<10}")
        
        # 趋势摘要
        trends = data.get("trends", {})
        overall = trends.get("overall", {})
        
        if overall:
            print("\n总体表现:")
            print(f"  平均胜率: {overall.get('avg_win_rate', 0)*100:.1f}%")
            print(f"  最高胜率: {overall.get('max_win_rate', 0)*100:.1f}%")
            print(f"  平均ROI: {overall.get('avg_roi', 0)*100:.1f}%")
            print(f"  最高ROI: {overall.get('max_roi', 0)*100:.1f}%")
        
        # 建议摘要
        recommendations = trends.get("recommendations", [])
        if recommendations:
            print("\n优化建议:")
            for rec in sorted(recommendations, key=lambda x: x["priority"], reverse=True):
                print(f"  [{rec['priority']}] {rec['strategy']}: {rec['action']} ({rec['reason']})")
        
        print("\n" + "="*70)
        print(f"Token使用: {self.token_usage['today']}/{self.token_usage['daily_limit']}")
        print("="*70)

# 主函数
if __name__ == "__main__":
    collector = StrategyDataCollector()
    data = collector.collect_all_strategy_data(days_back=7)
    
    # 生成优化任务
    print("\n生成优化任务...")
    recommendations = data.get("trends", {}).get("recommendations", [])
    
    if recommendations:
        high_priority = [r for r in recommendations if r["priority"] == "高"]
        if high_priority:
            print(f"发现 {len(high_priority)} 个高优先级优化任务")
            for task in high_priority:
                print(f"  - {task['strategy']}: {task['action']}")
    else:
        print("暂无高优先级优化任务")