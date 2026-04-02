# DeepSeek成本优化 - 立即实施方案

## 目标
基于DeepSeek最新回复，立即实施两个核心省钱机制：
1. **提示词缓存** - 90%折扣（\$0.028/百万token）
2. **上下文精简** - V3.2极低价格 + 高频调用成本几乎可忽略

## 当前状态分析
### 配置检查
- **当前模型**: `deepseek-chat` (需要确认是否为V3.2)
- **API端点**: `https://api.deepseek.com/v1`
- **可用模型**: `deepseek-chat`, `deepseek-reasoner` (R1)

### 成本优化机会
1. **提示词缓存未启用** - 系统提示、工具描述固定内容可缓存
2. **模型选择未优化** - 可能未使用最便宜的V3.2
3. **上下文未精简** - 可能携带不必要历史

## 立即实施措施

### 1. 启用提示词缓存 ✅（最高优先级）
**原理**: 量化交易的系统提示、工具描述通常是固定的，开启后这部分重复内容仅需 \$0.028/百万token

**实施步骤**:
```python
# 在API调用中启用提示词缓存
# DeepSeek API可能通过参数控制，需要检查文档
# 可能的参数: cache=True 或 prompt_caching=True
```

**检查点**:
- [ ] 查阅DeepSeek API文档，确认提示词缓存启用方式
- [ ] 修改OpenClaw配置，启用缓存
- [ ] 测试缓存效果，验证成本降低

### 2. 确认并切换到V3.2模型 ✅
**原理**: V3.2价格已经极低，配合缓存策略，高频调用成本几乎可忽略不计

**实施步骤**:
1. 确认当前`deepseek-chat`是否为V3.2版本
2. 如果不是，切换到V3.2模型
3. 测试模型性能和成本

**模型选择策略** (DeepSeek建议):
- **高频信号/简单判断**: 无脑选 V3.2，单次调用成本极低
- **复杂归因/策略推理**: 选 R1 (`deepseek-reasoner`)，虽然稍贵但比Claude仍是地板价

### 3. 实施上下文精简 ✅
**结合我们已有的优化**:
- [x] `MINIMAL_CONTEXT.md`指南 - 最小上下文原则
- [x] 工作流优化 - 结论+下一步+blocker回复结构
- [ ] 提示词模板化 - 固定格式减少变体

**新增措施**:
1. **系统提示精简**: 移除不必要描述，只保留核心指令
2. **工具描述压缩**: 量化工具描述精简到最小
3. **历史上下文管理**: 只保留最近关键决策

## 技术实现

### 配置修改方案
```json
{
  "models": {
    "providers": {
      "deepseek": {
        "baseUrl": "https://api.deepseek.com/v1",
        "apiKey": "sk-4f508f0198ac4d1ebbc068a78695c3a5",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek-chat",  // 确认是否为V3.2
            "name": "DeepSeek Chat V3.2",
            "parameters": {
              "prompt_caching": true,  // 假设参数名
              "cache_ttl": 3600  // 缓存1小时
            }
          },
          {
            "id": "deepseek-reasoner",
            "name": "DeepSeek Reasoner (R1)",
            "use_for": ["complex_reasoning", "strategy_analysis"]
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek/deepseek-chat",
        "fallback": "deepseek/deepseek-reasoner"
      },
      "context_optimization": {
        "max_history_turns": 3,
        "compress_system_prompt": true,
        "enable_prompt_caching": true
      }
    }
  }
}
```

### 提示词模板优化
```python
# 优化前（冗长）
system_prompt = """
你是一个量化交易助手，负责分析市场数据并提供交易建议。
你可以访问以下工具：数据获取、技术指标计算、风险评估等。
请仔细分析数据，给出详细的交易建议。
"""

# 优化后（精简 + 可缓存）
system_prompt = """
量化助手。分析数据，输出：action(buy/sell/hold) + reason(<20字)。
工具：data, indicators, risk。
"""
```

### 调用策略优化
```python
def optimize_api_call(prompt, model="deepseek-chat"):
    """优化API调用，启用缓存和精简"""
    params = {
        "model": model,
        "messages": [{"role": "system", "content": cached_system_prompt},
                     {"role": "user", "content": prompt}],
        "max_tokens": 50,  # 限制输出
        "temperature": 0.1,  # 低随机性
        # 假设的缓存参数
        "cache": True,
        "cache_key": generate_cache_key(prompt)
    }
    return call_api(params)
```

## 测试方案

### 测试1：缓存效果测试
```bash
# 发送相同提示词多次，观察响应时间和成本
python3 test_prompt_caching.py --iterations 10 --prompt "BTC分析"
```

### 测试2：模型成本对比
```bash
# 对比V3.2和R1的成本
python3 test_model_costs.py --model deepseek-chat --requests 100
python3 test_model_costs.py --model deepseek-reasoner --requests 100
```

### 测试3：上下文精简效果
```bash
# 测试不同上下文长度对成本的影响
python3 test_context_optimization.py --turns 1,3,5,10
```

## 预期效果

### 成本降低目标
| 优化措施 | 预期节省 | 时间框架 |
|----------|----------|----------|
| 提示词缓存 | 90% (固定内容) | 立即 |
| V3.2模型 | 极低成本 | 立即 |
| 上下文精简 | 50-70% | 1天 |
| 合计 | 95%+总成本 | 1周 |

### 量化指标
1. **token单价**: 从当前降至 \$0.028/百万token (缓存部分)
2. **调用频率**: 可大幅提升，成本几乎可忽略
3. **总成本**: 预期降低95%以上

## 实施时间表

### 今天（立即）
1. [ ] 确认DeepSeek API的缓存启用方式
2. [ ] 修改OpenClaw配置，启用优化
3. [ ] 测试基础功能，确保正常工作

### 明天
1. [ ] 部署优化后的提示词模板
2. [ ] 实施模型选择策略（V3.2 for 简单，R1 for 复杂）
3. [ ] 监控初始成本变化

### 本周
1. [ ] 全面部署优化方案
2. [ ] 建立成本监控仪表板
3. [ ] 评估优化效果，调整策略

## 风险与缓解

### 风险1：缓存导致响应过时
- **缓解**: 设置合理TTL，关键数据实时获取
- **缓解**: 价格波动大时绕过缓存

### 风险2：过度精简影响质量
- **缓解**: 关键决策保持必要上下文
- **缓解**: A/B测试优化前后质量

### 风险3：API变更
- **缓解**: 封装API调用，便于调整
- **缓解**: 监控API响应，及时适配

## 监控指标

### 成本监控
- 每日token消耗
- 缓存命中率
- 模型使用分布
- 成本节省百分比

### 质量监控
- 决策准确性
- 响应时间
- 用户满意度
- 策略收益影响

## 负责人
- 主要执行：当前助手
- 技术支持：DeepSeek文档
- 验收：Jim

## 更新记录
- 2026-03-20: 创建立即实施方案，基于DeepSeek最新建议
- 2026-03-20: 需要确认API具体参数和启用方式