# 策略优化迭代方案

## 🎯 目标
基于现有数据和结果，优化迭代策略：
1. **严格控制token使用** - 防止费用过高
2. **保证量化软件正常迭代** - 不断提高结果
3. **对比BR数据分析** - 优化出收益率接近的方案
4. **谨慎添加策略** - 策略版本反复更新迭代

## 📊 当前状态分析

### 策略配置现状
1. **PM策略 (4个)**:
   - `br_v2_highprob.json` - 高概率模式 (minPrice: 0.5, 关键词过滤)
   - `br_v2_brstyle.json` - BR风格
   - `br_v2_relaxed.json` - 宽松模式  
   - `br_v3_short.json` - 短周期模式

2. **CEX策略 (2个)**:
   - `cex_btc_5m_breakout_v1.json` - 突破策略 (breakoutLookback: 8, breakoutVolMult: 1.4)
   - `cex_btc_5m_reversion_v1.json` - 回归策略

3. **运行状态**:
   - PM策略: 运行中 (自动runner)
   - 数据产出: 641个PM文件，最近2小时25个新文件
   - CEX策略: 需要检查状态

### 问题识别
1. **缺乏结果数据** - 策略结果文件为空
2. **无BR对比数据** - 需要分析BR策略表现
3. **token使用未优化** - 需要集成缓存优化
4. **迭代机制缺失** - 需要建立版本迭代流程

## 🔧 策略优化迭代框架

### 1. 严格控制token使用
```python
# scripts/token_controlled_strategy_optimizer.py
"""
Token控制的策略优化器
确保在预算内进行策略优化迭代
"""

class TokenControlledOptimizer:
    def __init__(self, daily_token_budget=100000):  # 每日10万token
        self.daily_budget = daily_token_budget
        self.today_used = 0
        self.optimization_history = []
        
    def can_optimize(self, estimated_tokens):
        """检查是否可以进行优化"""
        if self.today_used + estimated_tokens > self.daily_budget:
            return False, f"预算不足: 已用{self.today_used}, 需要{estimated_tokens}"
        return True, "可以优化"
    
    def optimize_strategy(self, strategy_data, current_performance):
        """
        基于性能数据进行策略优化
        严格控制token使用
        """
        # 1. 估算token使用
        analysis_tokens = 500  # 分析数据
        optimization_tokens = 1000  # 生成优化方案
        total_tokens = analysis_tokens + optimization_tokens
        
        # 2. 检查预算
        can_optimize, message = self.can_optimize(total_tokens)
        if not can_optimize:
            return None, message
        
        # 3. 使用本地规则进行优化（避免LLM调用）
        optimizations = self._local_optimization(strategy_data, current_performance)
        
        # 4. 记录使用
        self.today_used += total_tokens
        self.optimization_history.append({
            "timestamp": time.time(),
            "strategy": strategy_data["name"],
            "tokens_used": total_tokens,
            "optimizations": optimizations
        })
        
        return optimizations, "优化完成"
    
    def _local_optimization(self, strategy, performance):
        """本地规则优化（无LLM调用）"""
        optimizations = []
        
        # 基于胜率优化
        if performance.get("win_rate", 0) < 0.5:
            optimizations.append({
                "type": "win_rate_low",
                "action": "收紧过滤条件",
                "params": ["minPrice: +0.1", "keywords: +严格"]
            })
        
        # 基于订单数优化
        if performance.get("total_orders", 0) < 10:
            optimizations.append({
                "type": "low_volume",
                "action": "放宽条件",
                "params": ["minPrice: -0.1", "maxMinsToEnd: +更多"]
            })
        
        # 基于PNL优化
        if performance.get("total_pnl", 0) < 0:
            optimizations.append({
                "type": "negative_pnl",
                "action": "调整参数",
                "params": ["sizeUSD: -50%", "requireAcceptingOrders: true"]
            })
        
        return optimizations
```

### 2. 策略版本迭代系统
```python
# scripts/strategy_version_manager.py
"""
策略版本管理器
支持谨慎添加、反复迭代、版本控制
"""

class StrategyVersionManager:
    def __init__(self, base_dir="strategies"):
        self.base_dir = Path(base_dir)
        self.version_history = {}
        
    def create_new_version(self, strategy_name, changes, reason):
        """
        创建新策略版本
        谨慎添加，必须有充分理由
        """
        # 1. 检查是否真的需要新版本
        current = self._load_current(strategy_name)
        if not self._needs_new_version(current, changes, reason):
            return None, "无需新版本，优化现有版本"
        
        # 2. 生成版本号
        version = self._generate_version(strategy_name)
        
        # 3. 创建新版本文件
        new_strategy = self._apply_changes(current, changes)
        new_filename = f"{strategy_name}_{version}.json"
        
        # 4. 保存并记录
        self._save_version(new_filename, new_strategy)
        self._record_version(strategy_name, version, changes, reason)
        
        return new_filename, f"版本 {version} 创建成功"
    
    def _needs_new_version(self, current, changes, reason):
        """检查是否需要新版本"""
        # 规则1: 必须有明确理由
        if not reason or len(reason) < 10:
            return False
        
        # 规则2: 必须有实质性变化
        significant_changes = sum(1 for change in changes if change.get("significant", False))
        if significant_changes < 1:
            return False
        
        # 规则3: 不能频繁创建版本
        last_version = self._get_last_version(current["name"])
        if last_version and time.time() - last_version["timestamp"] < 3600:  # 1小时内
            return False
        
        return True
    
    def _generate_version(self, strategy_name):
        """生成版本号: v{主版本}.{次版本}.{迭代号}"""
        if strategy_name not in self.version_history:
            return "v1.0.0"
        
        versions = self.version_history[strategy_name]
        last = versions[-1]["version"]
        
        # 解析版本号
        if last.startswith("v"):
            parts = last[1:].split(".")
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2]) if len(parts) > 2 else 0
            
            # 决定升级哪个部分
            if len(versions) % 5 == 0:  # 每5次迭代升主版本
                return f"v{major+1}.0.0"
            elif len(versions) % 2 == 0:  # 每2次迭代升次版本
                return f"v{major}.{minor+1}.0"
            else:  # 小迭代
                return f"v{major}.{minor}.{patch+1}"
        
        return "v1.0.0"
```

### 3. BR数据分析与对比
```python
# scripts/br_analysis_comparator.py
"""
BR数据分析与对比
优化出收益率接近BR的方案
"""

class BRAnalysisComparator:
    def __init__(self, br_data_path="data/br_reference"):
        self.br_data_path = Path(br_data_path)
        self.br_patterns = self._extract_br_patterns()
    
    def _extract_br_patterns(self):
        """提取BR策略模式"""
        # 从现有策略中提取BR特征
        patterns = {
            "filtering": {
                "min_price": 0.5,  # 最低价格
                "keywords": ["bitcoin", "btc", "ethereum", "eth"],
                "time_window": 525600  # 分钟
            },
            "position_sizing": {
                "size_usd": 50,
                "max_orders": 40
            },
            "risk_management": {
                "dedup_hours": 6,
                "require_accepting": False
            }
        }
        return patterns
    
    def compare_with_br(self, strategy_performance):
        """与BR策略对比"""
        comparison = {
            "similarity_score": 0.0,
            "differences": [],
            "recommendations": []
        }
        
        # 计算相似度
        similarity = self._calculate_similarity(strategy_performance)
        comparison["similarity_score"] = similarity
        
        # 识别差异
        if similarity < 0.7:  # 相似度低于70%
            differences = self._identify_differences(strategy_performance)
            comparison["differences"] = differences
            
            # 生成优化建议
            recommendations = self._generate_recommendations(differences)
            comparison["recommendations"] = recommendations
        
        return comparison
    
    def optimize_toward_br(self, current_strategy, target_similarity=0.8):
        """向BR策略优化"""
        optimizations = []
        
        # 1. 过滤条件优化
        if current_strategy.get("minPrice", 1) > self.br_patterns["filtering"]["min_price"]:
            optimizations.append({
                "parameter": "minPrice",
                "current": current_strategy.get("minPrice"),
                "target": self.br_patterns["filtering"]["min_price"],
                "action": "降低到BR水平"
            })
        
        # 2. 关键词优化
        current_keywords = set(current_strategy.get("keywords", []))
        br_keywords = set(self.br_patterns["filtering"]["keywords"])
        missing_keywords = br_keywords - current_keywords
        
        if missing_keywords:
            optimizations.append({
                "parameter": "keywords",
                "current": list(current_keywords),
                "target": list(br_keywords),
                "action": f"添加缺失关键词: {list(missing_keywords)}"
            })
        
        # 3. 仓位管理优化
        if current_strategy.get("sizeUSD", 0) != self.br_patterns["position_sizing"]["size_usd"]:
            optimizations.append({
                "parameter": "sizeUSD",
                "current": current_strategy.get("sizeUSD"),
                "target": self.br_patterns["position_sizing"]["size_usd"],
                "action": "调整到BR标准仓位"
            })
        
        return optimizations
```

## 🚀 执行计划

### 阶段一：数据收集与分析 (今天)
1. **收集现有策略数据**
   ```bash
   # 收集PM策略运行数据
   python3 scripts/collect_strategy_data.py --type pm --days 7
   
   # 收集CEX策略运行数据  
   python3 scripts/collect_strategy_data.py --type cex --days 7
   ```

2. **分析BR策略特征**
   ```bash
   # 分析BR策略模式
   python3 scripts/analyze_br_patterns.py --input strategies/br_*.json
   ```

3. **建立性能基准**
   ```bash
   # 建立性能基准线
   python3 scripts/establish_performance_baseline.py
   ```

### 阶段二：策略优化迭代 (今天)
1. **实施token控制优化**
   ```bash
   # 集成token控制优化器
   python3 scripts/integrate_token_control.py
   ```

2. **创建版本迭代系统**
   ```bash
   # 部署版本管理器
   python3 scripts/deploy_version_manager.py
   ```

3. **执行第一轮优化**
   ```bash
   # 基于数据优化策略
   python3 scripts/execute_strategy_optimization.py --strategy br_v2_highprob
   ```

### 阶段三：对比与优化 (今天)
1. **BR对比分析**
   ```bash
   # 与BR策略对比
   python3 scripts/compare_with_br.py --strategy all
   ```

2. **生成优化方案**
   ```bash
   # 生成接近BR的优化方案
   python3 scripts/generate_br_optimized_strategy.py
   ```

3. **测试新策略**
   ```bash
   # 测试优化后的策略
   python3 scripts/test_optimized_strategy.py --strategy br_optimized_v1
   ```

## 📈 优化指标

### Token使用控制
| 指标 | 目标 | 监控方法 |
|------|------|----------|
| 日token使用 | <100,000 | 实时监控 |
| 单次优化token | <2,000 | 预算检查 |
| 缓存命中率 | >60% | 缓存统计 |
| 成本节省 | >40% | 成本对比 |

### 策略迭代质量
| 指标 | 目标 | 监控方法 |
|------|------|----------|
| 版本迭代间隔 | >2小时 | 版本历史 |
| 实质性变化率 | >70% | 变化分析 |
| 性能提升率 | >10% | 前后对比 |
| BR相似度 | >80% | 对比分析 |

### 量化结果
| 指标 | 目标 | 监控方法 |
|------|------|----------|
| 胜率 | >55% | 结果统计 |
| ROI | >5% | PNL计算 |
| 订单数 | >20/天 | 订单统计 |
| 最大回撤 | <15% | 风险监控 |

## 🔧 技术实现

### 1. 数据收集管道
```python
# 自动收集策略数据
class StrategyDataCollector:
    def collect_performance_data(self):
        """收集策略性能数据"""
        # 从日志文件收集
        # 从数据库收集  
        # 从API收集
        pass
    
    def calculate_metrics(self):
        """计算关键指标"""
        metrics = {
            "win_rate": self._calculate_win_rate(),
            "roi": self._calculate_roi(),
            "sharpe_ratio": self._calculate_sharpe(),
            "max_drawdown": self._calculate_drawdown()
        }
        return metrics
```

### 2. 优化决策引擎
```python
# 基于规则的优化决策
class OptimizationDecisionEngine:
    def decide_optimization(self, strategy_data, performance):
        """决定是否优化及如何优化"""
        decisions = []
        
        # 规则1: 胜率低 → 收紧过滤
        if performance["win_rate"] < 0.5:
            decisions.append({
                "type": "tighten_filters",
                "confidence": 0.8,
                "actions": ["increase_min_price", "add_keywords"]
            })
        
        # 规则2: 订单少 → 放宽条件
        if performance["total_orders"] < 10:
            decisions.append({
                "type": "loosen_filters", 
                "confidence": 0.7,
                "actions": ["decrease_min_price", "extend_time_window"]
            })
        
        # 规则3: 亏损 → 减小仓位
        if performance["total_pnl"] < 0:
            decisions.append({
                "type": "reduce_risk",
                "confidence": 0.9,
                "actions": ["decrease_position_size", "enable_stop_loss"]
            })
        
        return decisions
```

### 3. 版本控制与回滚
```python
# 安全的版本控制
class SafeVersionController:
    def create_version(self, strategy, changes):
        """创建新版本"""
        # 1. 验证变化
        if not self._validate_changes(changes):
            return None, "变化验证失败"
        
        # 2. 创建备份
        backup_id = self._create_backup(strategy)
        
        # 3. 应用变化
        new_version = self._apply_changes(strategy, changes)
        
        # 4. 记录版本
        version_id = self._record_version(strategy, changes, backup_id)
        
        return version_id, "版本创建成功"
    
    def rollback_if_needed(self, new_version, old_performance, new_performance):
        """如果需要则回滚"""
        # 检查性能下降
        if new_performance["win_rate"] < old_performance["win_rate"] * 0.8:
            return self._rollback_to_backup(new_version)
        
        if new_performance["roi"] < old_performance["roi"] * 0.5:
            return self._rollback_to_back