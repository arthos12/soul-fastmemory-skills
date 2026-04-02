#!/usr/bin/env python3
"""
基于BR分析的策略优化器
对比BR数据，优化出收益率接近的方案
严格控制token使用，谨慎添加策略
"""

import json
import time
from datetime import datetime
from pathlib import Path
import hashlib

class BRBasedStrategyOptimizer:
    """基于BR分析的策略优化器"""
    
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.strategies_dir = self.workspace / "strategies"
        self.output_dir = self.workspace / "strategies" / "optimized"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # BR策略特征（从现有策略中提取）
        self.br_patterns = self._extract_br_patterns()
        
        # Token使用控制
        self.token_budget = {
            "daily_limit": 20000,  # 每日2万token（严格控制）
            "used_today": 0,
            "last_reset": time.time()
        }
        
        # 优化历史
        self.optimization_history = []
    
    def _extract_br_patterns(self):
        """从现有BR策略中提取模式"""
        patterns = {
            "filtering": {
                "min_price_range": [0.4, 0.6],  # BR通常使用0.5
                "common_keywords": [
                    "bitcoin", "btc", "ethereum", "eth", "solana", "sol",
                    "xrp", "doge", "dogecoin", "bnb", "avax", "cardano", "ada"
                ],
                "time_window": 525600,  # 1年
                "max_orders": 40
            },
            "risk_management": {
                "position_size": 50,  # 50美元
                "dedup_hours": 6,
                "require_accepting": False
            },
            "performance_targets": {
                "min_win_rate": 0.55,
                "min_roi": 0.05,
                "max_drawdown": 0.15
            }
        }
        return patterns
    
    def analyze_current_strategies(self):
        """分析当前策略与BR的差距"""
        print("分析当前策略与BR的差距...")
        print("="*70)
        
        strategies = self._load_all_strategies()
        analysis_results = {}
        
        for name, strategy in strategies.items():
            print(f"\n分析策略: {name}")
            
            # 计算与BR的相似度
            similarity = self._calculate_br_similarity(strategy)
            
            # 识别差距
            gaps = self._identify_gaps(strategy)
            
            # 生成优化建议
            recommendations = self._generate_recommendations(strategy, gaps)
            
            analysis_results[name] = {
                "similarity_score": similarity,
                "gaps": gaps,
                "recommendations": recommendations,
                "optimization_priority": self._calculate_priority(similarity, gaps)
            }
            
            print(f"  相似度: {similarity:.1%}")
            print(f"  差距数: {len(gaps)}")
            print(f"  优化优先级: {analysis_results[name]['optimization_priority']}")
        
        return analysis_results
    
    def _load_all_strategies(self):
        """加载所有策略"""
        strategies = {}
        for file in self.strategies_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    strategy = json.load(f)
                    strategies[file.stem] = strategy
            except:
                continue
        return strategies
    
    def _calculate_br_similarity(self, strategy):
        """计算与BR策略的相似度"""
        similarity = 0.0
        total_weights = 0
        
        # 1. 价格过滤相似度 (权重: 30%)
        min_price = strategy.get("minPrice", 1.0)
        br_min_price = self.br_patterns["filtering"]["min_price_range"][0]
        price_diff = abs(min_price - br_min_price)
        price_similarity = max(0, 1 - price_diff / 0.5)  # 差异在0.5以内
        similarity += price_similarity * 0.3
        total_weights += 0.3
        
        # 2. 关键词相似度 (权重: 25%)
        keywords = set(strategy.get("keywords", []))
        br_keywords = set(self.br_patterns["filtering"]["common_keywords"])
        if keywords and br_keywords:
            keyword_overlap = len(keywords & br_keywords) / len(br_keywords)
            similarity += keyword_overlap * 0.25
        total_weights += 0.25
        
        # 3. 仓位管理相似度 (权重: 20%)
        size_usd = strategy.get("sizeUSD", 0)
        br_size = self.br_patterns["risk_management"]["position_size"]
        if size_usd > 0:
            size_similarity = 1 - abs(size_usd - br_size) / br_size
            similarity += max(0, size_similarity) * 0.2
        total_weights += 0.2
        
        # 4. 风险管理相似度 (权重: 15%)
        dedup = strategy.get("dedupLookbackHours", 0)
        br_dedup = self.br_patterns["risk_management"]["dedup_hours"]
        if dedup > 0:
            dedup_similarity = 1 - abs(dedup - br_dedup) / br_dedup
            similarity += max(0, dedup_similarity) * 0.15
        total_weights += 0.15
        
        # 5. 订单限制相似度 (权重: 10%)
        max_orders = strategy.get("maxOrders", 0)
        br_max_orders = self.br_patterns["filtering"]["max_orders"]
        if max_orders > 0:
            orders_similarity = 1 - abs(max_orders - br_max_orders) / br_max_orders
            similarity += max(0, orders_similarity) * 0.1
        total_weights += 0.1
        
        # 归一化
        if total_weights > 0:
            similarity /= total_weights
        
        return similarity
    
    def _identify_gaps(self, strategy):
        """识别与BR策略的差距"""
        gaps = []
        
        # 1. 价格过滤差距
        min_price = strategy.get("minPrice", 1.0)
        br_target = self.br_patterns["filtering"]["min_price_range"][0]
        if abs(min_price - br_target) > 0.1:
            gaps.append({
                "parameter": "minPrice",
                "current": min_price,
                "target": br_target,
                "gap": abs(min_price - br_target),
                "importance": "高"
            })
        
        # 2. 关键词差距
        keywords = set(strategy.get("keywords", []))
        br_keywords = set(self.br_patterns["filtering"]["common_keywords"])
        missing_keywords = br_keywords - keywords
        if missing_keywords:
            gaps.append({
                "parameter": "keywords",
                "current": list(keywords),
                "target": list(br_keywords),
                "gap": f"缺失{len(missing_keywords)}个关键词",
                "importance": "中"
            })
        
        # 3. 仓位差距
        size_usd = strategy.get("sizeUSD", 0)
        br_size = self.br_patterns["risk_management"]["position_size"]
        if size_usd != br_size:
            gaps.append({
                "parameter": "sizeUSD",
                "current": size_usd,
                "target": br_size,
                "gap": abs(size_usd - br_size),
                "importance": "高"
            })
        
        # 4. 去重时间差距
        dedup = strategy.get("dedupLookbackHours", 0)
        br_dedup = self.br_patterns["risk_management"]["dedup_hours"]
        if dedup != br_dedup:
            gaps.append({
                "parameter": "dedupLookbackHours",
                "current": dedup,
                "target": br_dedup,
                "gap": abs(dedup - br_dedup),
                "importance": "中"
            })
        
        return gaps
    
    def _generate_recommendations(self, strategy, gaps):
        """生成优化建议"""
        recommendations = []
        
        for gap in gaps:
            param = gap["parameter"]
            current = gap["current"]
            target = gap["target"]
            
            if param == "minPrice":
                action = "降低" if current > target else "提高"
                recommendations.append({
                    "parameter": param,
                    "action": f"{action}到{target}",
                    "reason": f"当前{current}，BR标准{target}",
                    "priority": gap["importance"]
                })
            
            elif param == "keywords":
                recommendations.append({
                    "parameter": param,
                    "action": "添加缺失的关键词",
                    "reason": gap["gap"],
                    "priority": gap["importance"]
                })
            
            elif param == "sizeUSD":
                action = "减少" if current > target else "增加"
                recommendations.append({
                    "parameter": param,
                    "action": f"{action}到{target}美元",
                    "reason": f"当前{current}美元，BR标准{target}美元",
                    "priority": gap["importance"]
                })
            
            elif param == "dedupLookbackHours":
                action = "缩短" if current > target else "延长"
                recommendations.append({
                    "parameter": param,
                    "action": f"{action}到{target}小时",
                    "reason": f"当前{current}小时，BR标准{target}小时",
                    "priority": gap["importance"]
                })
        
        return recommendations
    
    def _calculate_priority(self, similarity, gaps):
        """计算优化优先级"""
        if similarity >= 0.8 and len(gaps) <= 1:
            return "低"
        elif similarity >= 0.6 and len(gaps) <= 3:
            return "中"
        else:
            return "高"
    
    def optimize_strategy(self, strategy_name, original_strategy, recommendations):
        """优化单个策略"""
        print(f"\n优化策略: {strategy_name}")
        
        # 检查token预算
        estimated_tokens = 1000  # 估算优化所需token
        if not self._check_token_budget(estimated_tokens):
            print("  Token预算不足，跳过优化")
            return None
        
        # 创建优化后的策略
        optimized = original_strategy.copy()
        
        # 应用高优先级建议
        high_priority = [r for r in recommendations if r["priority"] == "高"]
        medium_priority = [r for r in recommendations if r["priority"] == "中"]
        
        changes_applied = []
        
        # 先应用高优先级
        for rec in high_priority[:2]:  # 最多应用2个高优先级变化
            success = self._apply_recommendation(optimized, rec)
            if success:
                changes_applied.append(rec)
        
        # 如果有余量，应用中优先级
        if len(changes_applied) < 3:  # 总共最多3个变化
            for rec in medium_priority[:3 - len(changes_applied)]:
                success = self._apply_recommendation(optimized, rec)
                if success:
                    changes_applied.append(rec)
        
        if not changes_applied:
            print("  未应用任何优化")
            return None
        
        # 生成版本号
        version = self._generate_version(strategy_name, changes_applied)
        
        # 保存优化后的策略
        optimized["name"] = f"{original_strategy.get('name', strategy_name)}_{version}"
        optimized["optimized_from"] = strategy_name
        optimized["optimization_date"] = datetime.now().isoformat()
        optimized["changes_applied"] = [r["action"] for r in changes_applied]
        
        output_file = self.output_dir / f"{strategy_name}_{version}.json"
        with open(output_file, 'w') as f:
            json.dump(optimized, f, indent=2)
        
        # 记录token使用
        self._record_token_usage(estimated_tokens)
        
        # 记录优化历史
        self.optimization_history.append({
            "timestamp": time.time(),
            "strategy": strategy_name,
            "version": version,
            "changes": changes_applied,
            "file": str(output_file)
        })
        
        print(f"  优化完成: {version}")
        print(f"  应用变化: {len(changes_applied)} 个")
        print(f"  保存到: {output_file}")
        
        return optimized
    
    def _apply_recommendation(self, strategy, recommendation):
        """应用单个优化建议"""
        param = recommendation["parameter"]
        action = recommendation["action"]
        
        try:
            if param == "minPrice":
                # 解析目标值
                if "到" in action:
                    target_str = action.split("到")[1]
                    target = float(target_str)
                    strategy["minPrice"] = target
                    return True
            
            elif param == "keywords":
                if "添加" in action:
                    # 添加缺失的关键词
                    current = set(strategy.get("keywords", []))
                    br_keywords = set(self.br_patterns["filtering"]["common_keywords"])
                    missing = br_keywords - current
                    if missing:
                        strategy["keywords"] = list(current | missing)
                        return True
            
            elif param == "sizeUSD":
                if "到" in action:
                    target_str = action.split("到")[0]  # "50美元"
                    target = int(target_str.replace("美元", ""))
                    strategy["sizeUSD"] = target
                    return True
            
            elif param == "dedupLookbackHours":
                if "到" in action:
                    target_str = action.split("到")[0]  # "6小时"
                    target = int(target_str.replace("小时", ""))
                    strategy["dedupLookbackHours"] = target
                    return True
        
        except:
            pass
        
        return False
    
    def _generate_version(self, strategy_name, changes):
        """生成版本号"""
        # 基于变化内容生成哈希
        change_hash = hashlib.md5(
            str([c["action"] for c in changes]).encode()
        ).hexdigest()[:6]
        
        # 获取当前日期
        date_str = datetime.now().strftime("%y%m%d")
        
        return f"v{date_str}_{change_hash}"
    
    def _check_token_budget(self, estimated_tokens):
        """检查token预算"""
        # 每日重置
        if time.time() - self.token_budget["last_reset"] > 86400:
            self.token_budget["used_today"] = 0
            self.token_budget["last_reset"] = time.time()
        
        if self.token_budget["used_today"] + estimated_tokens > self.token_budget["daily_limit"]:
            return False
        
        return True
    
    def _record_token_usage(self, tokens):
        """记录token使用"""
        self.token_budget["used_today"] += tokens
    
    def run_optimization_pipeline(self):
        """运行完整的优化管道"""
        print("基于BR分析的策略优化管道")
        print("="*70)
        
        # 1. 分析当前策略
        analysis = self.analyze_current_strategies()
        
        # 2. 按优先级排序
        strategies_to_optimize = []
        for name, data in analysis.items():
            if data["optimization_priority"] in ["高", "中"]:
                strategies_to_optimize.append((name, data))
        
        # 按优先级排序：高 -> 中
        strategies_to_optimize.sort(
            key=lambda x: 0 if x[1]["optimization_priority"] == "高" else 1
        )
        
        print(f"\n需要优化的策略: {len(strategies_to_optimize)} 个")
        
        # 3. 优化策略（严格控制数量）
        optimized_strategies = []
        max_optimizations = 3  # 每次最多优化3个策略
        
        for i, (name, data) in enumerate(strategies_to_optimize[:max_optimizations]):
            print(f"\n[{i+1}/{min(len(strategies_to_optimize), max_optimizations)}] 优化策略")
            
            # 加载原始策略
            strategies = self._load_all_strategies()
            if name in strategies:
                original = strategies[name]
                
                # 执行优化
                optimized = self.optimize_strategy(name, original, data["recommendations"])
                if optimized:
                    optimized_strategies.append(optimized)
        
        # 4. 生成报告
        self.generate_optimization_report(analysis, optimized_strategies)
        
        return optimized_strategies
    
    def generate_optimization_report(self, analysis, optimized_strategies):
        """生成优化报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": {},
            "optimizations_performed": len(optimized_strategies),
            "token_usage": self.token_budget["used_today"],
            "details": {}
        }
        
        # 分析摘要
        priorities = {"高": 0, "中": 0, "低": 0}
        for data in analysis.values():
            priorities[data["optimization_priority"]] += 1
        
        report["analysis_summary"] = {
            "total_strategies": len(analysis),
            "high_priority": priorities["高"],
            "medium_priority": priorities["中"],
            "low_priority": priorities["低"],
            "avg_similarity": sum(d["similarity_score"] for d in analysis.values()) / len(analysis)
        }
        
        # 优化详情
        for strategy in optimized