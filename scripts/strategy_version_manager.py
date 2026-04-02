#!/usr/bin/env python3
"""
策略版本管理器
实现自适应量化软件的策略版本体系
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class StrategyVersionManager:
    """策略版本管理器"""
    
    def __init__(self, db_path: str = "data/strategy_versions.json"):
        self.db_path = db_path
        self.ensure_db()
    
    def ensure_db(self):
        """确保数据库文件存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"strategies": {}, "versions": {}}, f, indent=2)
    
    def load_db(self) -> Dict:
        """加载数据库"""
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def save_db(self, data: Dict):
        """保存数据库"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_version_name(self, strategy_id: str, parent_version: Optional[str] = None) -> str:
        """创建版本名（含UTC时间戳）"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if parent_version:
            # 基于父版本创建新版本
            base_name = parent_version.split("_")[0]  # 提取基础名称
            return f"{base_name}_{timestamp}"
        else:
            # 全新版本
            return f"{strategy_id}_v1_{timestamp}"
    
    def register_strategy(self, strategy_id: str, strategy_type: str, description: str = ""):
        """注册新策略"""
        data = self.load_db()
        
        if strategy_id not in data["strategies"]:
            data["strategies"][strategy_id] = {
                "id": strategy_id,
                "type": strategy_type,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "current_version": None,
                "versions": []
            }
            self.save_db(data)
            print(f"✅ 注册策略: {strategy_id}")
    
    def create_version(self, strategy_id: str, params: Dict, 
                      parent_version: Optional[str] = None,
                      hypothesis: str = "") -> str:
        """创建新版本"""
        data = self.load_db()
        
        if strategy_id not in data["strategies"]:
            print(f"❌ 策略未注册: {strategy_id}")
            return None
        
        # 创建版本名
        version_name = self.create_version_name(strategy_id, parent_version)
        
        # 创建版本记录
        version_data = {
            "version": version_name,
            "strategy_id": strategy_id,
            "parent_version": parent_version,
            "created_at_utc": datetime.utcnow().isoformat(),
            "changed_params": params,
            "hypothesis": hypothesis,
            "status": "testing",
            "metrics": {
                "sample_n": 0,
                "win_rate": 0.0,
                "roi_after_cost": 0.0,
                "drawdown_proxy": 0.0,
                "orders_per_day": 0.0,
                "trades_per_day": 0.0
            },
            "performance_history": []
        }
        
        # 保存到数据库
        if "versions" not in data:
            data["versions"] = {}
        
        data["versions"][version_name] = version_data
        data["strategies"][strategy_id]["versions"].append(version_name)
        data["strategies"][strategy_id]["current_version"] = version_name
        
        self.save_db(data)
        print(f"✅ 创建版本: {version_name}")
        print(f"   策略: {strategy_id}")
        print(f"   父版本: {parent_version or '无'}")
        print(f"   参数: {json.dumps(params, indent=2)}")
        
        return version_name
    
    def update_metrics(self, version_name: str, metrics: Dict):
        """更新版本指标"""
        data = self.load_db()
        
        if version_name in data["versions"]:
            # 更新指标
            data["versions"][version_name]["metrics"].update(metrics)
            
            # 添加到历史记录
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics.copy()
            }
            data["versions"][version_name]["performance_history"].append(history_entry)
            
            self.save_db(data)
            print(f"✅ 更新指标: {version_name}")
            print(f"   指标: {json.dumps(metrics, indent=2)}")
        else:
            print(f"❌ 版本不存在: {version_name}")
    
    def promote_version(self, version_name: str):
        """提升版本状态（testing → promoted）"""
        data = self.load_db()
        
        if version_name in data["versions"]:
            data["versions"][version_name]["status"] = "promoted"
            self.save_db(data)
            print(f"✅ 提升版本: {version_name} → promoted")
        else:
            print(f"❌ 版本不存在: {version_name}")
    
    def reject_version(self, version_name: str, reason: str = ""):
        """拒绝版本（testing → rejected）"""
        data = self.load_db()
        
        if version_name in data["versions"]:
            data["versions"][version_name]["status"] = "rejected"
            data["versions"][version_name]["rejection_reason"] = reason
            self.save_db(data)
            print(f"✅ 拒绝版本: {version_name} → rejected")
            if reason:
                print(f"   原因: {reason}")
        else:
            print(f"❌ 版本不存在: {version_name}")
    
    def compare_versions(self, version_a: str, version_b: str) -> Dict:
        """比较两个版本"""
        data = self.load_db()
        
        if version_a not in data["versions"] or version_b not in data["versions"]:
            print(f"❌ 版本不存在: {version_a} 或 {version_b}")
            return None
        
        version_a_data = data["versions"][version_a]
        version_b_data = data["versions"][version_b]
        
        comparison = {
            "version_a": version_a,
            "version_b": version_b,
            "strategy_id": version_a_data["strategy_id"],
            "comparison_timestamp": datetime.utcnow().isoformat(),
            "metrics_comparison": {},
            "param_differences": self._compare_params(
                version_a_data["changed_params"],
                version_b_data["changed_params"]
            )
        }
        
        # 比较指标
        for metric in ["win_rate", "roi_after_cost", "orders_per_day"]:
            val_a = version_a_data["metrics"].get(metric, 0)
            val_b = version_b_data["metrics"].get(metric, 0)
            comparison["metrics_comparison"][metric] = {
                "version_a": val_a,
                "version_b": val_b,
                "difference": val_b - val_a,
                "improvement": val_b > val_a if metric != "drawdown_proxy" else val_b < val_a
            }
        
        return comparison
    
    def _compare_params(self, params_a: Dict, params_b: Dict) -> Dict:
        """比较参数差异"""
        all_keys = set(params_a.keys()) | set(params_b.keys())
        differences = {}
        
        for key in all_keys:
            val_a = params_a.get(key)
            val_b = params_b.get(key)
            
            if val_a != val_b:
                differences[key] = {
                    "version_a": val_a,
                    "version_b": val_b,
                    "changed": True
                }
            else:
                differences[key] = {
                    "version_a": val_a,
                    "version_b": val_b,
                    "changed": False
                }
        
        return differences
    
    def get_best_version(self, strategy_id: str, metric: str = "roi_after_cost") -> Optional[str]:
        """获取最佳版本"""
        data = self.load_db()
        
        if strategy_id not in data["strategies"]:
            return None
        
        best_version = None
        best_value = -float('inf')
        
        for version_name in data["strategies"][strategy_id]["versions"]:
            if version_name in data["versions"]:
                version_data = data["versions"][version_name]
                if version_data["status"] == "promoted":
                    value = version_data["metrics"].get(metric, 0)
                    if value > best_value:
                        best_value = value
                        best_version = version_name
        
        return best_version
    
    def print_strategy_tree(self, strategy_id: str):
        """打印策略版本树"""
        data = self.load_db()
        
        if strategy_id not in data["strategies"]:
            print(f"❌ 策略不存在: {strategy_id}")
            return
        
        print(f"\n🌳 策略版本树: {strategy_id}")
        print("="*60)
        
        versions = data["strategies"][strategy_id]["versions"]
        
        # 构建版本树
        version_tree = {}
        for version_name in versions:
            if version_name in data["versions"]:
                version_data = data["versions"][version_name]
                parent = version_data["parent_version"]
                
                if parent not in version_tree:
                    version_tree[parent] = []
                version_tree[parent].append(version_name)
        
        # 打印树状结构
        def print_tree(node: str, depth: int = 0):
            if node in version_tree:
                for child in version_tree[node]:
                    if child in data["versions"]:
                        child_data = data["versions"][child]
                        prefix = "  " * depth + "├─ " if depth > 0 else "└─ "
                        status_symbol = {
                            "testing": "🟡",
                            "promoted": "✅",
                            "rejected": "❌",
                            "paused": "⏸️"
                        }.get(child_data["status"], "❓")
                        
                        print(f"{prefix}{status_symbol} {child}")
                        print(f"{'  ' * (depth + 1)}创建: {child_data['created_at_utc']}")
                        print(f"{'  ' * (depth + 1)}状态: {child_data['status']}")
                        print(f"{'  ' * (depth + 1)}ROI: {child_data['metrics'].get('roi_after_cost', 0):.2%}")
                        
                        # 递归打印子节点
                        print_tree(child, depth + 1)
        
        # 从根节点开始（parent_version为None）
        print_tree(None)

# 使用示例
if __name__ == "__main__":
    # 初始化管理器
    manager = StrategyVersionManager()
    
    # 注册策略
    manager.register_strategy("cex_btc_5m_breakout", "cex", "BTC 5分钟突破策略")
    manager.register_strategy("pm_br_v2_relaxed", "pm", "PM BR宽松版策略")
    
    # 创建版本
    version1 = manager.create_version(
        strategy_id="cex_btc_5m_breakout",
        params={"window": 5, "threshold": 0.5, "max_position": 0.1},
        hypothesis="5分钟窗口，0.5%突破阈值"
    )
    
    # 更新指标
    if version1:
        manager.update_metrics(version1, {
            "sample_n": 100,
            "win_rate": 0.55,
            "roi_after_cost": 0.012,
            "orders_per_day": 24.5
        })
        
        # 提升版本
        manager.promote_version(version1)
    
    # 创建新版本（基于父版本）
    version2 = manager.create_version(
        strategy_id="cex_btc_5m_breakout",
        params={"window": 5, "threshold": 0.3, "max_position": 0.1},  # 降低阈值
        parent_version=version1,
        hypothesis="降低阈值到0.3%，提高频率"
    )
    
    # 打印策略树
    manager.print_strategy_tree("cex_btc_5m_breakout")
    
    print("\n✅ 策略版本管理器初始化完成")