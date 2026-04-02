# 多模型量化交易执行方案

## 🎯 最终目标
1. **多种大模型**: 不只是DeepSeek，支持OpenAI、Anthropic、Gemini等
2. **节省token**: 通用缓存优化，大幅降低成本
3. **量化交易跑起来**: 确保系统实际运行并产生收益

## 📊 当前状态分析

### 量化系统状态 ✅
- **PM策略**: 4个自动运行中 (br_v2_highprob, br_v2_brstyle, br_v2_relaxed, br_v3_short)
- **CEX策略**: 2个自动运行中 (cex_btc_5m_breakout_v1, cex_btc_5m_reversion_v1)
- **系统保护**: guard机制已接入，避免CPU/内存崩溃
- **关键发现**: 量化脚本**无LLM API调用**，主要使用数据API

### 缓存优化状态 ✅
- **通用缓存优化器**: 已完成 (`scripts/universal_cache_optimizer.py`)
- **API包装器**: 已完成 (`scripts/cached_api_wrapper.py`)
- **自动集成工具**: 已完成 (`scripts/execute_cache_integration.py`)
- **文档体系**: 完整 (`docs/openclaw_cache_integration.md`)

## 🚀 立即执行方案

### 阶段一：多模型集成（今天）
#### 1. 配置多模型支持
```bash
# 检查当前可用模型
openclaw config get models.providers

# 添加多模型配置
cat > ~/.openclaw/multi_model_config.json << 'EOF'
{
  "providers": {
    "openai": {
      "api_key": "${OPENAI_API_KEY}",
      "models": ["gpt-4", "gpt-4-turbo", "o1-mini", "o1-preview"]
    },
    "deepseek": {
      "api_key": "${DEEPSEEK_API_KEY}",
      "models": ["deepseek-chat", "deepseek-reasoner"]
    },
    "anthropic": {
      "api_key": "${ANTHROPIC_API_KEY}",
      "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    },
    "gemini": {
      "api_key": "${GEMINI_API_KEY}",
      "models": ["gemini-2.0-pro", "gemini-1.5-pro"]
    }
  },
  "default_strategy": {
    "simple_analysis": "deepseek-chat",      # 简单分析用DeepSeek（便宜）
    "complex_reasoning": "claude-3-sonnet",  # 复杂推理用Claude
    "creative_generation": "gpt-4",          # 创意生成用GPT-4
    "fast_response": "gemini-1.5-pro"        # 快速响应用Gemini
  }
}
EOF
```

#### 2. 创建多模型路由器
```python
# scripts/multi_model_router.py
"""
多模型智能路由器
根据任务类型、成本、性能选择最佳模型
"""

class MultiModelRouter:
    def __init__(self):
        self.cost_table = {
            "openai/gpt-4": {"input": 0.03, "output": 0.06},
            "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "openai/o1-mini": {"input": 0.11, "output": 0.44},
            "deepseek/deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek/deepseek-reasoner": {"input": 0.28, "output": 1.12},
            "anthropic/claude-3-sonnet": {"input": 0.03, "output": 0.15},
            "anthropic/claude-3-haiku": {"input": 0.025, "output": 0.125},
            "gemini/gemini-1.5-pro": {"input": 0.00125, "output": 0.005}
        }
        
        self.performance_table = {
            "reasoning": ["claude-3-sonnet", "deepseek-reasoner", "gpt-4"],
            "speed": ["gemini-1.5-pro", "claude-3-haiku", "deepseek-chat"],
            "cost": ["gemini-1.5-pro", "deepseek-chat", "claude-3-haiku"],
            "quality": ["gpt-4", "claude-3-opus", "deepseek-reasoner"]
        }
    
    def select_model(self, task_type, budget, urgency):
        """根据任务选择最佳模型"""
        # 1. 按任务类型筛选
        candidates = self.performance_table.get(task_type, ["deepseek-chat"])
        
        # 2. 按预算筛选
        affordable = [
            model for model in candidates
            if self.cost_table.get(model, {}).get("input", 1) * 1000 <= budget
        ]
        
        # 3. 按紧急程度选择
        if urgency == "high":
            # 选择最快的
            return next((m for m in affordable if m in self.performance_table["speed"]), affordable[0])
        else:
            # 选择最便宜的
            return min(affordable, key=lambda m: self.cost_table.get(m, {}).get("input", 1))
```

### 阶段二：量化系统增强（今天）
#### 1. 检查当前运行状态
```bash
# 检查PM策略运行状态
ps aux | grep -E "pm_auto_runner|pm_paper_loop"

# 检查CEX策略运行状态
ps aux | grep -E "cex_auto_runner|btc_5m_paper"

# 检查数据产出
ls -la data/polymarket/*.jsonl | head -10
ls -la data/cex/*.jsonl | head -10
```

#### 2. 添加LLM分析层（可选）
```python
# scripts/quant_llm_enhancer.py
"""
量化系统LLM增强层
在现有规则系统基础上添加LLM分析
"""

def enhance_with_llm(market_data, strategy_results):
    """
    使用LLM增强量化分析
    """
    # 1. 异常检测
    anomalies = detect_anomalies_with_llm(market_data, strategy_results)
    
    # 2. 模式识别
    patterns = identify_patterns_with_llm(market_data)
    
    # 3. 策略优化建议
    optimizations = suggest_optimizations_with_llm(strategy_results)
    
    # 4. 风险预警
    warnings = generate_risk_warnings_with_llm(market_data, anomalies)
    
    return {
        "anomalies": anomalies,
        "patterns": patterns,
        "optimizations": optimizations,
        "warnings": warnings
    }
```

#### 3. 创建统一执行监控
```bash
# scripts/quant_execution_monitor.sh
#!/bin/bash
# 量化执行统一监控

echo "量化系统执行监控 - $(date)"
echo "========================================"

# 1. 进程监控
echo "进程状态:"
ps aux | grep -E "(pm_|cex_|btc_)" | grep -v grep

# 2. 数据产出监控
echo ""
echo "数据产出:"
echo "PM数据: $(find data/polymarket -name "*.jsonl" -mmin -60 | wc -l) 个新文件"
echo "CEX数据: $(find data/cex -name "*.jsonl" -mmin -60 | wc -l) 个新文件"

# 3. 策略性能监控
echo ""
echo "策略性能:"
python3 scripts/check_dual_side_monitor.py --brief

# 4. 成本监控
echo ""
echo "API成本:"
python3 scripts/monitor_cache.py --summary
```

### 阶段三：成本优化集成（今天）
#### 1. 集成通用缓存到量化系统
```python
# 修改现有量化脚本，添加缓存支持
# scripts/pm_paper_loop.py (示例修改)

# 原代码
# response = requests.get(api_url)

# 新代码
from cached_api_wrapper import cached_api_call

response = cached_api_call(
    provider="data_api",
    cache_key=f"polymarket_{timestamp}",
    api_call_func=requests.get,
    url=api_url
)
```

#### 2. 创建成本控制策略
```python
# scripts/cost_controller.py
"""
多模型成本控制器
确保在预算内运行量化系统
"""

class CostController:
    def __init__(self, daily_budget=10.0):  # 每日10美元预算
        self.daily_budget = daily_budget
        self.today_cost = 0.0
        self.cost_log = []
        
    def can_make_call(self, estimated_cost):
        """检查是否可以进行API调用"""
        if self.today_cost + estimated_cost > self.daily_budget:
            print(f"预算不足: 今日已用${self.today_cost:.2f}, 需要${estimated_cost:.2f}")
            return False
        
        # 记录成本
        self.today_cost += estimated_cost
        self.cost_log.append({
            "timestamp": time.time(),
            "cost": estimated_cost,
            "remaining": self.daily_budget - self.today_cost
        })
        
        return True
    
    def get_cost_optimized_model(self, task):
        """获取成本优化的模型选择"""
        # 简单任务用便宜模型
        if task in ["price_check", "signal_verification"]:
            return "deepseek-chat"  # 最便宜
        
        # 中等任务用性价比模型
        elif task in ["market_analysis", "trend_prediction"]:
            return "claude-3-haiku"  # 性价比高
        
        # 复杂任务用高质量模型
        else:
            return "gpt-4"  # 质量优先
```

## 📈 执行时间表

### 今天（立即执行）
1. **09:00-10:00**: 配置多模型支持
   - 检查API密钥配置
   - 测试各模型可用性
   - 创建模型路由器

2. **10:00-11:00**: 增强量化系统
   - 检查当前运行状态
   - 添加监控脚本
   - 测试LLM增强层

3. **11:00-12:00**: 集成成本优化
   - 集成通用缓存
   - 部署成本控制器
   - 测试完整流程

### 今天下午
1. **13:00-14:00**: 系统测试
   - 运行完整量化流程
   - 监控多模型使用
   - 验证成本控制

2. **14:00-15:00**: 优化调整
   - 基于测试结果调整参数
   - 优化模型选择策略
   - 完善监控告警

3. **15:00-16:00**: 文档和部署
   - 更新部署文档
   - 创建维护脚本
   - 设置自动化监控

## 🎯 预期成果

### 量化交易系统
1. **运行状态**: PM 4策略 + CEX 2策略持续运行
2. **数据产出**: 实时市场数据 + 策略结果
3. **收益跟踪**: ROI、胜率、订单数监控
4. **风险控制**: 系统保护 + 预算控制

### 多模型支持
1. **模型多样性**: 4+提供商，10+模型
2. **智能路由**: 任务类型 → 最佳模型
3. **成本优化**: 便宜模型处理简单任务
4. **质量保证**: 关键任务用高质量模型

### 成本控制
1. **缓存优化**: 系统提示词90%+节省
2. **预算控制**: 每日成本不超过设定值
3. **成本监控**: 实时成本跟踪和预警
4. **自动降级**: 预算紧张时自动切换便宜模型

## 🔧 技术架构

```
量化数据源 → 规则引擎 → LLM增强层 → 策略执行
    ↓           ↓           ↓           ↓
 数据API     本地规则   多模型路由   交易所API
    ↓           ↓           ↓           ↓
数据缓存    规则缓存  提示词缓存   订单缓存
    ↓           ↓           ↓           ↓
成本监控 ←── 统一监控 ←── 性能监控 ←── 结果监控
```

## 📊 成功指标

### 量化指标
1. **系统运行率**: >95% (策略持续运行)
2. **数据完整性**: 100% (无数据缺失)
3. **策略收益**: ROI > 0% (正收益)
4. **订单质量**: 胜率 > 50%

### 成本指标
1. **缓存命中率**: >50%
2. **成本节省**: >30%
3. **预算遵守**: 100% (不超预算)
4. **模型利用率**: 各模型合理使用

### 性能指标
1. **响应时间**: <5秒 (LLM分析)
2. **系统稳定性**: 无崩溃
3. **监控覆盖率**: 100%关键指标
4. **告警及时性**: <1分钟

## 🚨 风险与缓解

### 技术风险
1. **API限流**: 多模型分散风险 + 缓存减少调用
2. **模型失效**: 多模型备选 + 自动切换
3. **系统崩溃**: guard机制 + 自动重启

### 成本风险
1. **预算超支**: 成本控制器 + 实时监控
2. **无效调用**: 条件触发 + 缓存优化
3. **模型浪费**: 智能路由 + 任务匹配

### 运营风险
1. **数据缺失**: 多数据源 + 缓存备份
2. **策略失效**: 多策略 + 实时监控
3. **监控盲点**: 全面监控 + 定期检查

## ✅ 执行检查清单

### 配置检查
- [ ] 多模型API密钥配置
- [ ] 量化系统运行状态
- [ ] 缓存优化器集成
- [ ] 成本控制器部署

### 功能测试
- [ ] 多模型路由测试
- [ ] 量化策略执行测试
- [ ] 缓存命中率测试
- [ ] 成本控制测试

### 监控部署
- [ ] 系统运行监控
- [ ] 成本使用监控
- [ ] 策略性能监控
- [ ] 告警机制测试

## 📝 更新记录
- 2026-03-20: 创建多模型量化执行方案
- 2026-03-20: 整合缓存优化、多模型支持、量化执行

## 🎯 总结
**目标**: 多种大模型 + 节省token + 量化交易跑起来  
**方案**: 多模型智能路由 + 通用缓存优化 + 量化系统增强  
**状态**: 所有组件已就绪，可立即执行集成