#!/usr/bin/env python3
"""
执行监控器
监控执行延迟、价格漂移，并实现执行闸门
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics

class ExecutionMonitor:
    """执行监控器"""
    
    def __init__(self, db_path: str = "data/execution_metrics.json"):
        self.db_path = db_path
        self.ensure_db()
    
    def ensure_db(self):
        """确保数据库文件存在"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"executions": [], "summary": {}}, f, indent=2)
    
    def load_db(self) -> Dict:
        """加载数据库"""
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def save_db(self, data: Dict):
        """保存数据库"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_execution(self, strategy_id: str, version: str,
                        signal_data: Dict, execution_data: Dict) -> str:
        """记录一次执行"""
        execution_id = f"exec_{int(time.time())}_{strategy_id}"
        
        # 计算关键指标
        metrics = self._calculate_metrics(signal_data, execution_data)
        
        execution_record = {
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_id": strategy_id,
            "version": version,
            "signal_data": signal_data,
            "execution_data": execution_data,
            "metrics": metrics,
            "status": "completed" if execution_data.get("filled", False) else "rejected"
        }
        
        # 保存到数据库
        data = self.load_db()
        data["executions"].append(execution_record)
        
        # 更新摘要统计
        self._update_summary(data, strategy_id, metrics)
        
        self.save_db(data)
        
        print(f"📝 记录执行: {execution_id}")
        print(f"   策略: {strategy_id} ({version})")
        print(f"   状态: {execution_record['status']}")
        print(f"   延迟: {metrics.get('decision_latency_ms', 0):.1f}ms")
        print(f"   漂移: {metrics.get('price_drift_bps', 0):.1f}bps")
        
        return execution_id
    
    def _calculate_metrics(self, signal_data: Dict, execution_data: Dict) -> Dict:
        """计算执行指标"""
        metrics = {}
        
        # 时间戳
        signal_time = signal_data.get("signal_timestamp", time.time())
        decision_time = signal_data.get("decision_timestamp", time.time())
        submit_time = execution_data.get("submit_timestamp", time.time())
        fill_time = execution_data.get("fill_timestamp", time.time())
        
        # 价格
        signal_price = signal_data.get("signal_price", 0)
        confirm_price = execution_data.get("confirm_price", 0)
        fill_price = execution_data.get("fill_price", 0)
        
        # 计算延迟（毫秒）
        if signal_time and decision_time:
            metrics["decision_latency_ms"] = (decision_time - signal_time) * 1000
        
        if decision_time and submit_time:
            metrics["submit_latency_ms"] = (submit_time - decision_time) * 1000
        
        if submit_time and fill_time:
            metrics["fill_latency_ms"] = (fill_time - submit_time) * 1000
        
        if signal_time and fill_time:
            metrics["total_latency_ms"] = (fill_time - signal_time) * 1000
        
        # 计算价格漂移（基点）
        if signal_price and confirm_price and signal_price > 0:
            drift_pct = (confirm_price - signal_price) / signal_price
            metrics["signal_to_confirm_drift_bps"] = drift_pct * 10000  # 转换为基点
        
        if confirm_price and fill_price and confirm_price > 0:
            drift_pct = (fill_price - confirm_price) / confirm_price
            metrics["confirm_to_fill_drift_bps"] = drift_pct * 10000
        
        if signal_price and fill_price and signal_price > 0:
            drift_pct = (fill_price - signal_price) / signal_price
            metrics["total_price_drift_bps"] = drift_pct * 10000
        
        # 计算滑点（如果可用）
        if "slippage" in execution_data:
            metrics["slippage_bps"] = execution_data["slippage"] * 10000
        
        # 计算成本
        if "fee" in execution_data:
            metrics["fee_bps"] = execution_data["fee"] * 10000
        
        return metrics
    
    def _update_summary(self, data: Dict, strategy_id: str, metrics: Dict):
        """更新摘要统计"""
        if "summary" not in data:
            data["summary"] = {}
        
        if strategy_id not in data["summary"]:
            data["summary"][strategy_id] = {
                "total_executions": 0,
                "completed": 0,
                "rejected": 0,
                "avg_decision_latency_ms": 0,
                "avg_total_latency_ms": 0,
                "avg_price_drift_bps": 0,
                "max_price_drift_bps": 0,
                "rejection_reasons": {}
            }
        
        summary = data["summary"][strategy_id]
        summary["total_executions"] += 1
        
        # 更新延迟统计
        if "decision_latency_ms" in metrics:
            current_avg = summary["avg_decision_latency_ms"]
            total = summary["completed"] + summary["rejected"]
            summary["avg_decision_latency_ms"] = (
                (current_avg * total + metrics["decision_latency_ms"]) / (total + 1)
            )
        
        if "total_latency_ms" in metrics:
            current_avg = summary["avg_total_latency_ms"]
            total = summary["completed"] + summary["rejected"]
            summary["avg_total_latency_ms"] = (
                (current_avg * total + metrics["total_latency_ms"]) / (total + 1)
            )
        
        # 更新价格漂移统计
        if "total_price_drift_bps" in metrics:
            drift = metrics["total_price_drift_bps"]
            current_avg = summary["avg_price_drift_bps"]
            total = summary["completed"]
            if drift != 0:  # 只统计已完成的
                summary["avg_price_drift_bps"] = (
                    (current_avg * total + drift) / (total + 1)
                )
                summary["max_price_drift_bps"] = max(summary["max_price_drift_bps"], abs(drift))
    
    def check_execution_gate(self, strategy_id: str, signal_data: Dict, 
                           current_market_data: Dict) -> Tuple[bool, str]:
        """检查执行闸门"""
        rejection_reasons = []
        
        # 1. 检查信号TTL（生存时间）
        signal_age = time.time() - signal_data.get("signal_timestamp", 0)
        signal_ttl = signal_data.get("signal_ttl_seconds", 30)  # 默认30秒
        
        if signal_age > signal_ttl:
            rejection_reasons.append(f"信号过期 ({signal_age:.1f}s > {signal_ttl}s)")
        
        # 2. 检查价格漂移阈值
        signal_price = signal_data.get("signal_price", 0)
        current_price = current_market_data.get("price", 0)
        
        if signal_price > 0 and current_price > 0:
            price_drift_pct = abs(current_price - signal_price) / signal_price
            drift_threshold = signal_data.get("drift_threshold_bps", 50) / 10000  # 默认50bps
            
            if price_drift_pct > drift_threshold:
                rejection_reasons.append(
                    f"价格漂移超阈值 ({price_drift_pct*10000:.1f}bps > {drift_threshold*10000}bps)"
                )
        
        # 3. 检查edge（预期收益）
        expected_edge = signal_data.get("expected_edge_bps", 0)
        min_edge_threshold = signal_data.get("min_edge_threshold_bps", 10)  # 默认10bps
        
        if expected_edge < min_edge_threshold:
            rejection_reasons.append(f"edge过薄 ({expected_edge}bps < {min_edge_threshold}bps)")
        
        # 4. 检查市场流动性
        if "liquidity" in current_market_data:
            min_liquidity = signal_data.get("min_liquidity", 10000)
            if current_market_data["liquidity"] < min_liquidity:
                rejection_reasons.append(
                    f"流动性不足 ({current_market_data['liquidity']} < {min_liquidity})"
                )
        
        # 5. 检查波动率
        if "volatility" in current_market_data:
            max_volatility = signal_data.get("max_volatility_bps", 200)  # 默认200bps
            if current_market_data["volatility"] > max_volatility:
                rejection_reasons.append(
                    f"波动率过高 ({current_market_data['volatility']}bps > {max_volatility}bps)"
                )
        
        # 决定是否通过闸门
        if rejection_reasons:
            return False, "; ".join(rejection_reasons)
        else:
            return True, "通过所有检查"
    
    def get_performance_report(self, strategy_id: str, 
                              lookback_hours: int = 24) -> Dict:
        """获取性能报告"""
        data = self.load_db()
        
        # 筛选指定时间范围内的执行记录
        cutoff_time = time.time() - (lookback_hours * 3600)
        
        recent_executions = [
            e for e in data["executions"]
            if e["strategy_id"] == strategy_id and 
            time.mktime(datetime.fromisoformat(e["timestamp"]).timetuple()) > cutoff_time
        ]
        
        if not recent_executions:
            return {"error": "无近期执行记录"}
        
        # 计算统计指标
        completed = [e for e in recent_executions if e["status"] == "completed"]
        rejected = [e for e in recent_executions if e["status"] == "rejected"]
        
        report = {
            "period_hours": lookback_hours,
            "total_executions": len(recent_executions),
            "completed": len(completed),
            "rejected": len(rejected),
            "completion_rate": len(completed) / len(recent_executions) if recent_executions else 0,
            "latency_stats": {},
            "drift_stats": {},
            "rejection_analysis": {}
        }
        
        # 延迟统计
        if completed:
            latencies = [e["metrics"].get("total_latency_ms", 0) for e in completed]
            report["latency_stats"] = {
                "avg_ms": statistics.mean(latencies) if latencies else 0,
                "median_ms": statistics.median(latencies) if latencies else 0,
                "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0,
                "max_ms": max(latencies) if latencies else 0
            }
        
        # 价格漂移统计
        if completed:
            drifts = [abs(e["metrics"].get("total_price_drift_bps", 0)) for e in completed]
            report["drift_stats"] = {
                "avg_bps": statistics.mean(drifts) if drifts else 0,
                "median_bps": statistics.median(drifts) if drifts else 0,
                "p95_bps": statistics.quantiles(drifts, n=20)[18] if len(drifts) >= 20 else 0,
                "max_bps": max(drifts) if drifts else 0
            }
        
        # 拒绝原因分析
        rejection_reasons = {}
        for exec in rejected:
            if "rejection_reason" in exec:
                reason = exec["rejection_reason"]
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        report["rejection_analysis"] = rejection_reasons
        
        return report
    
    def print_recent_executions(self, strategy_id: str, limit: int = 10):
        """打印最近执行记录"""
        data = self.load_db()
        
        executions = [
            e for e in data["executions"]
            if e["strategy_id"] == strategy_id
        ]
        
        # 按时间排序
        executions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        print(f"\n📋 最近执行记录: {strategy_id}")
        print("="*80)
        
        for i, exec in enumerate(executions[:limit]):
            status_symbol = "✅" if exec["status"] == "completed" else "❌"
            print(f"{i+1}. {status_symbol} {exec['execution_id']}")
            print(f"   时间: {exec['timestamp']}")
            print(f"   版本: {exec['version']}")
            print(f"   状态: {exec['status']}")
            
            metrics = exec["metrics"]
            if "total_latency_ms" in metrics:
                print(f"   总延迟: {metrics['total_latency_ms']:.1f}ms")
            if "total_price_drift_bps" in metrics:
                print(f"   价格漂移: {metrics['total_price_drift_bps']:.1f}bps")
            
            if exec["status"] == "rejected" and "rejection_reason" in exec:
                print(f"   拒绝原因: {exec['rejection_reason']}")
            
            print()

# 使用示例
if __name__ == "__main__":
    monitor = ExecutionMonitor()
    
    # 模拟一次执行记录
    signal_data = {
        "signal_timestamp": time.time() - 2.5,
        "decision_timestamp": time.time() - 2.0,
        "signal_price": 50000.0,
        "signal_ttl_seconds": 30,
        "drift_threshold_bps": 50,
        "expected_edge_bps": 25,
        "min_edge_threshold_bps": 10
    }
    
    execution_data = {
        "submit_timestamp": time.time() - 1.5,
        "fill_timestamp": time.time() - 1.0,
        "confirm_price": 50002.5,
        "fill_price": 50003.0,
        "filled": True,
        "fee": 0.001,
        "slippage": 0.0001
    }
    
    # 记录执行
    exec_id = monitor.record_execution(
        strategy_id="cex_btc_5m_breakout",
        version="v1_20260320_031408",
        signal_data=signal_data,
        execution_data=execution_data
    )
    
    # 测试执行闸门
    current_market = {
        "price": 50005.0,
        "liquidity": 50000,
        "volatility": 150
    }
    
    passed, reason = monitor.check_execution_gate(
        strategy_id="cex_btc_5m_breakout",
        signal_data=signal_data,
        current_market_data=current_market
    )
    
    print(f"\n🚦 执行闸门检查: {'✅ 通过' if passed else '❌ 拒绝'}")
    if not passed:
        print(f"   原因: {reason}")
    
    # 获取性能报告
    report = monitor.get_performance_report("cex_btc_5m_breakout", lookback_hours=1)
    
    print(f"\n📊 性能报告 (最近1小时)")
    print(f"总执行: {report.get('total_executions', 0)}")
    print(f"完成率: {report.get('completion_rate', 0):.1%}")
    
    if "latency_stats" in report:
        latency = report["latency_stats"]
        print(f"平均延迟: {latency.get('avg_ms', 0):.1f}ms")
    
    if "drift_stats" in report:
        drift = report["drift_stats"]
        print(f"平均漂移: {drift.get('avg_bps', 0):.1f}bps")
    
    # 打印最近执行记录
    monitor.print_recent_executions("cex_btc_5m_breakout", limit=5)
    
    print("\n✅ 执行监控器演示完成")