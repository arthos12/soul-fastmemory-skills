#!/usr/bin/env python3
"""
量化执行统一监控
监控多模型量化系统的运行状态、成本、性能
"""

import os
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

class QuantExecutionMonitor:
    """量化执行监控器"""
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.data_dir = self.workspace / "data"
        self.scripts_dir = self.workspace / "scripts"
        
        # 监控配置
        self.config = {
            "check_interval": 300,  # 5分钟检查一次
            "alert_thresholds": {
                "no_data_hours": 2,  # 2小时无数据告警
                "high_cpu_percent": 80,  # CPU使用率80%告警
                "high_memory_percent": 80,  # 内存使用率80%告警
                "cost_daily_limit": 10.0,  # 每日成本限制10美元
            },
            "monitor_components": {
                "pm_strategies": True,
                "cex_strategies": True,
                "data_pipelines": True,
                "llm_enhancements": True,
                "cache_performance": True,
                "cost_usage": True
            }
        }
        
        # 状态存储
        self.status = {
            "last_check": None,
            "alerts": [],
            "metrics": {},
            "trends": {}
        }
    
    def check_pm_strategies(self):
        """检查PM策略运行状态"""
        metrics = {
            "running": False,
            "process_count": 0,
            "data_files": 0,
            "last_data_time": None
        }
        
        try:
            # 检查进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('pm_' in str(arg) for arg in cmdline):
                        metrics["process_count"] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics["running"] = metrics["process_count"] > 0
            
            # 检查数据文件
            pm_data_dir = self.data_dir / "polymarket"
            if pm_data_dir.exists():
                now = time.time()
                recent_files = []
                for file in pm_data_dir.glob("*.jsonl"):
                    if now - file.stat().st_mtime < 3600:  # 1小时内
                        recent_files.append(file)
                
                metrics["data_files"] = len(recent_files)
                if recent_files:
                    latest = max(recent_files, key=lambda f: f.stat().st_mtime)
                    metrics["last_data_time"] = datetime.fromtimestamp(
                        latest.stat().st_mtime
                    ).isoformat()
            
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def check_cex_strategies(self):
        """检查CEX策略运行状态"""
        metrics = {
            "running": False,
            "process_count": 0,
            "data_files": 0,
            "last_data_time": None
        }
        
        try:
            # 检查进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('cex_' in str(arg) or 'btc_' in str(arg) for arg in cmdline):
                        metrics["process_count"] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics["running"] = metrics["process_count"] > 0
            
            # 检查数据文件
            cex_data_dir = self.data_dir / "cex"
            if cex_data_dir.exists():
                now = time.time()
                recent_files = []
                for file in cex_data_dir.glob("*.jsonl"):
                    if now - file.stat().st_mtime < 3600:  # 1小时内
                        recent_files.append(file)
                
                metrics["data_files"] = len(recent_files)
                if recent_files:
                    latest = max(recent_files, key=lambda f: f.stat().st_mtime)
                    metrics["last_data_time"] = datetime.fromtimestamp(
                        latest.stat().st_mtime
                    ).isoformat()
            
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def check_system_resources(self):
        """检查系统资源"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
        
        # 检查量化相关进程资源
        quant_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name']
                if any(keyword in name for keyword in ['python', 'pm_', 'cex_', 'btc_']):
                    quant_processes.append({
                        "pid": proc.info['pid'],
                        "name": name,
                        "cpu": proc.info['cpu_percent'],
                        "memory": proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        metrics["quant_processes"] = quant_processes
        metrics["quant_cpu_total"] = sum(p["cpu"] for p in quant_processes)
        metrics["quant_memory_total"] = sum(p["memory"] for p in quant_processes)
        
        return metrics
    
    def check_cache_performance(self):
        """检查缓存性能"""
        metrics = {
            "cache_db_exists": False,
            "cache_entries": 0,
            "cache_hit_rate": 0.0
        }
        
        try:
            # 检查缓存数据库
            cache_db = Path("/tmp/llm_cache.db")
            if cache_db.exists():
                metrics["cache_db_exists"] = True
                
                # 尝试读取缓存统计
                cache_report = self.workspace / "docs" / "cache_report.json"
                if cache_report.exists():
                    with open(cache_report, 'r') as f:
                        report = json.load(f)
                        metrics.update({
                            "cache_hit_rate": report.get("stats", {}).get("hit_rate", 0),
                            "tokens_saved": report.get("stats", {}).get("tokens_saved", 0),
                            "cost_saved": report.get("stats", {}).get("cost_saved", 0)
                        })
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def check_cost_usage(self):
        """检查成本使用"""
        metrics = {
            "daily_estimate": 0.0,
            "models_used": [],
            "cost_breakdown": {}
        }
        
        try:
            # 检查多模型路由器统计
            router_stats = self.workspace / "data" / "model_router_stats.json"
            if router_stats.exists():
                with open(router_stats, 'r') as f:
                    stats = json.load(f)
                    metrics.update({
                        "daily_estimate": stats.get("total_cost", 0.0),
                        "models_used": list(stats.get("by_model", {}).keys()),
                        "total_calls": stats.get("total_calls", 0)
                    })
        
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
    
    def generate_alerts(self, metrics):
        """生成告警"""
        alerts = []
        
        # PM策略告警
        pm = metrics.get("pm_strategies", {})
        if not pm.get("running", False):
            alerts.append({
                "level": "WARNING",
                "component": "PM_STRATEGIES",
                "message": "PM策略未运行",
                "timestamp": datetime.now().isoformat()
            })
        
        if pm.get("data_files", 0) == 0:
            alerts.append({
                "level": "WARNING",
                "component": "PM_DATA",
                "message": "PM无数据产出",
                "timestamp": datetime.now().isoformat()
            })
        
        # CEX策略告警
        cex = metrics.get("cex_strategies", {})
        if not cex.get("running", False):
            alerts.append({
                "level": "WARNING",
                "component": "CEX_STRATEGIES",
                "message": "CEX策略未运行",
                "timestamp": datetime.now().isoformat()
            })
        
        # 系统资源告警
        system = metrics.get("system_resources", {})
        if system.get("cpu_percent", 0) > self.config["alert_thresholds"]["high_cpu_percent"]:
            alerts.append({
                "level": "WARNING",
                "component": "SYSTEM_CPU",
                "message": f"CPU使用率过高: {system['cpu_percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        if system.get("memory_percent", 0) > self.config["alert_thresholds"]["high_memory_percent"]:
            alerts.append({
                "level": "WARNING",
                "component": "SYSTEM_MEMORY",
                "message": f"内存使用率过高: {system['memory_percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 成本告警
        cost = metrics.get("cost_usage", {})
        if cost.get("daily_estimate", 0) > self.config["alert_thresholds"]["cost_daily_limit"]:
            alerts.append({
                "level": "CRITICAL",
                "component": "COST",
                "message": f"日成本超过限制: ${cost['daily_estimate']:.2f}",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def run_check(self):
        """运行一次完整检查"""
        print(f"量化执行监控检查 - {datetime.now().isoformat()}")
        print("="*70)
        
        metrics = {}
        
        # 检查各组件
        if self.config["monitor_components"]["pm_strategies"]:
            metrics["pm_strategies"] = self.check_pm_strategies()
        
        if self.config["monitor_components"]["cex_strategies"]:
            metrics["cex_strategies"] = self.check_cex_strategies()
        
        metrics["system_resources"] = self.check_system_resources()
        
        if self.config["monitor_components"]["cache_performance"]:
            metrics["cache_performance"] = self.check_cache_performance()
        
        if self.config["monitor_components"]["cost_usage"]:
            metrics["cost_usage"] = self.check_cost_usage()
        
        # 生成告警
        alerts = self.generate_alerts(metrics)
        
        # 更新状态
        self.status = {
            "last_check": datetime.now().isoformat(),
            "alerts": alerts,
            "metrics": metrics,
            "summary": self.generate_summary(metrics, alerts)
        }
        
        # 打印结果
        self.print_results(metrics, alerts)
        
        # 保存状态
        self.save_status()
        
        return self.status
    
    def generate_summary(self, metrics, alerts):
        """生成摘要"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "components": {},
            "alert_count": len(alerts)
        }
        
        # 评估各组件状态
        components = {}
        
        # PM策略
        pm = metrics.get("pm_strategies", {})
        components["pm_strategies"] = {
            "status": "HEALTHY" if pm.get("running") and pm.get("data_files", 0) > 0 else "UNHEALTHY",
            "running": pm.get("running", False),
            "data_files": pm.get("data_files", 0)
        }
        
        # CEX策略
        cex = metrics.get("cex_strategies", {})
        components["cex_strategies"] = {
            "status": "HEALTHY" if cex.get("running") and cex.get("data_files", 0) > 0 else "UNHEALTHY",
            "running": cex.get("running", False),
            "data_files": cex.get("data_files", 0)
        }
        
        # 系统资源
        system = metrics.get("system_resources", {})
        components["system_resources"] = {
            "status": "HEALTHY" if system.get("cpu_percent", 0) < 80 and system.get("memory_percent", 0) < 80 else "WARNING",
            "cpu_percent": system.get("cpu_percent", 0),
            "memory_percent": system.get("memory_percent", 0)
        }
        
        # 缓存性能
        cache = metrics.get("cache_performance", {})
        components["cache_performance"] = {
            "status": "HEALTHY" if cache.get("cache_db_exists", False) else "NOT_CONFIGURED",
            "cache_hit_rate": cache.get("cache_hit_rate", 0)
        }
        
        summary["components"] = components
        
        # 总体状态
        unhealthy = sum(1 for c in components.values() if c["status"] == "UNHEALTHY")
        warnings = sum(1 for c in components.values() if c["status"] == "WARNING")
        
        if unhealthy > 0:
            summary["overall_status"] = "UNHEALTHY"
        elif warnings > 0:
            summary["overall_status"] = "WARNING"
        elif len(alerts) > 0:
            summary["overall_status"] = "WARNING"
        else:
            summary["overall_status"] = "HEALTHY"
        
        return summary
    
    def print_results(self, metrics, alerts):
        """打印检查结果"""
        
        # 摘要
        summary = self.generate_summary(metrics, alerts)
        print(f"总体状态: {summary['overall_status']}")
        print(f"告警数量: {len(alerts)}")
        print()
        
        # PM策略
        pm = metrics.get("pm_strategies", {})
        print("PM策略:")
        print(f"  运行状态: {'✅ 运行中' if pm.get('running') else '❌ 未运行'}")
        print(f"  进程数量: {pm.get('process_count', 0)}")
        print(f"  数据文件: {pm.get('data_files', 0)} 个 (最近1小时)")
        if pm.get('last_data_time'):
            print(f"  最后数据: {pm['last_data_time']}")
        print()
        
        # CEX策略
        cex = metrics.get("cex_strategies", {})
        print("CEX策略:")
        print(f"  运行状态: {'✅ 运行中' if cex.get('running') else '❌ 未运行'}")
        print(f"  进程数量: {cex.get('process_count', 0)}")
        print(f"  数据文件: {cex.get('data_files', 0)} 个 (最近1小时)")
        if cex.get('last_data_time'):
            print(f"  最后数据: {cex['last_data_time']}")
        print()
        
        # 系统资源
        system = metrics.get("system_resources", {})
        print("系统资源:")
        print(f"  CPU使用率: {system.get('cpu_percent', 0):.1f}%")
        print(f"  内存使用率: {system.get('memory_percent', 0):.1f}%")
        print(f"  磁盘使用率: {system.get('disk_usage', 0):.1f}%")
        print(f"  量化进程CPU: {system.get('quant_cpu_total', 0):.1f}%")
        print(f"  量化进程内存: {system.get('quant_memory_total', 0):.1f}%")
        print()
        
        # 缓存性能
        cache = metrics.get("cache_performance", {})
        print("缓存性能:")
        print(f"  缓存数据库: {'✅ 存在' if cache.get('cache_db_exists') else '❌ 不存在'}")
        print(f"  缓存命中率: {cache.get('cache_hit_rate', 0):.1%}")
        print(f"  节省Tokens: {cache.get('tokens_saved', 0):,}")
        print(f"  节省成本: ${cache.get('cost_saved', 0):.6f}")
        print()
        
        # 成本使用
        cost = metrics.get("cost_usage", {})
        print("成本使用:")
        print(f"  日成本估算: ${cost.get('daily_estimate', 0):.6f}")
        print(f"  总调用次数: {cost.get('total_calls', 0)}")
        print(f"  使用模型: {', '.join(cost.get('models_used', []))}")
        print()
        
        # 告警
        if alerts:
            print("⚠️  告警:")
            for alert in alerts:
                print(f"  [{alert['level']}] {alert['component']}: {alert['message']}")
            print()
        
        print("="*70)
    
    def save_status(self):
        """保存状态到文件"""
        status_file = self.workspace / "data" / "monitor_status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(status_file, 'w') as f:
            json.dump(self.status, f, indent=2, default=str)
    
    def run_continuous(self, interval=None):
        """持续运行监控"""
        if interval is None:
            interval = self.config["check_interval"]
        
        print(f"启动量化执行监控，检查间隔