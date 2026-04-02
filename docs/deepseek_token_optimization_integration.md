# DeepSeek Token优化建议整合

## 来源
DeepSeek针对量化交易bot的token优化建议，2026-03-20。

## 核心建议总结

### 一、数据输入优化：只喂"精华"，不喂"原矿"
**问题**: 原始行情数据（K线、订单簿）非常冗长
**解决方案**:
1. **技术指标替代原始K线**
   - 原: 100根1分钟K线 → 1000+ tokens
   - 优: 计算关键指标 → 20-30 tokens
   - 示例: "当前BTC: 45000 USDT, MA5: 44850, MA20: 44600, RSI(14): 62"

2. **压缩订单簿数据**
   - 原: 50档买卖盘 → 几百tokens
   - 优: 前3档 + 买卖压力比 → 少量tokens
   - 示例: "买一 45000 (2 BTC)，卖一 45005 (1.5 BTC)，买卖比1.3"

3. **定时摘要而非实时全量**
   - 触发条件: 价格波动>1% 或 RSI进入超买/超卖区
   - 效果: 减少90%以上调用

### 二、提示词工程：让AI"说重点"
1. **明确约束输出格式和长度**
   ```python
   system_prompt = """
   你是一个量化交易助手。请严格遵守以下规则：
   1. 只输出"买入"、"卖出"、"持有"三选一，不要解释。
   2. 若需要解释，必须控制在20字以内。
   3. 输出格式: {"action": "buy", "reason": "价格突破阻力位"}
   """
   ```

2. **使用指令模板**
   - 场景A（入场信号）: "当前价格X，MA5=Y，RSI=Z，是否适合开多？只回答YES/NO。"
   - 场景B（止损检查）: "持仓成本C，当前价格P，止损线SL，是否触发止损？只回答YES/NO。"

3. **设置max_tokens**
   - API调用时设置max_tokens=10~50
   - 防止AI输出长篇大论

### 三、调用策略：减少无效调用
1. **降频轮询**
   - 原: 1秒1次 → 优: 1分钟1次
   - 关键时段临时提高频率

2. **合并多个分析请求**
   ```python
   # 原: 分别调用BTC、ETH、SOL
   # 优: 一次请求同时分析多个币种
   prompt = """
   请分析以下三个币种当前趋势，分别给出buy/sell/hold建议：
   BTC: 45000, MA5:44850, RSI:62
   ETH: 3200, MA5:3180, RSI:58
   SOL: 110, MA5:108, RSI:65
   输出JSON: {"BTC":"...","ETH":"...","SOL":"..."}
   """
   ```

3. **设置调用冷却时间**
   - AI给出建议后，5分钟内不再重复调用同一品种

### 四、上下文管理：避免历史累积
1. **无状态调用**
   - 大多数场景使用独立调用，不传历史上下文

2. **短期记忆仅保留关键决策**
   - 只保留最近1轮对话
   - 或手动摘要历史: "之前你建议等待突破，现价格已突破45000，是否追入？"

3. **定时重置会话**
   - 每10次调用或每1小时清空历史

### 五、缓存机制：避免重复计算
1. **本地缓存相同输入的结果**
   - 1分钟内相同问题直接返回缓存结果

2. **相似数据去重**
   - 价格变动<0.1%时沿用上次分析结果

### 六、监控与持续优化
1. **利用开放平台日志**
   - 定期查看DeepSeek平台日志，分析token消耗

2. **A/B测试**
   - 对比优化前后的token消耗和策略收益

3. **动态调整参数**
   - 根据市场波动率动态调整调用频率

### 七、技术实现示例（Python伪代码）
```python
import time
from deepseek import DeepSeekAPI

client = DeepSeekAPI(api_key="your_key")

# 缓存字典
cache = {}
last_call_time = {}

def get_market_summary(symbol):
    # 获取实时数据并计算指标
    price = get_price(symbol)
    ma5 = calculate_ma(symbol, 5)
    rsi = calculate_rsi(symbol)
    return f"{symbol}: {price}, MA5: {ma5}, RSI: {rsi}"

def should_call_ai(symbol):
    # 判断是否满足调用条件
    if time.time() - last_call_time.get(symbol, 0) < 60:  # 至少间隔60秒
        return False
    price_change = abs(get_price_change(symbol))
    if price_change < 0.5:  # 价格变动小于0.5%不调用
        return False
    return True

def query_ai(symbol):
    if not should_call_ai(symbol):
        return cache.get(symbol, "no_update")

    # 构造精简输入
    summary = get_market_summary(symbol)
    prompt = f"根据以下数据，给出交易建议（buy/sell/hold）：{summary}"
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5  # 限制输出长度
    )
    
    result = response.choices[0].message.content
    cache[symbol] = result
    last_call_time[symbol] = time.time()
    return result
```

## 与当前系统整合情况

### ✅ 已完成整合
1. **量化系统无LLM API调用** ✅
   - 所有45个Python脚本检查完成
   - 主要使用数据API（Gamma、Binance）
   - 符合"无LLM API"原则

2. **工作流优化** ✅
   - 创建`MINIMAL_CONTEXT.md`指南
   - 更新AGENTS.md会话启动流程
   - 实施"结论+下一步+blocker"回复结构

3. **文档体系** ✅
   - `tasks/token_optimization_plan.md` - 整合DeepSeek建议
   - `checklists/token_optimization_checklist.md` - 每日检查清单

### 🔄 待实施（第二阶段）
1. **数据输入优化**
   - 技术指标替代原始K线
   - 压缩订单簿数据
   - 定时摘要而非实时全量

2. **提示词工程优化**
   - 明确约束输出格式
   - 使用指令模板
   - 设置max_tokens

3. **调用策略优化**
   - 降频轮询
   - 合并多个分析请求
   - 设置调用冷却时间

### 📊 预期效果（DeepSeek评估）
- **token消耗降低**: 50%~90%
- **调用频率减少**: 90%以上（通过条件触发）
- **决策准确性**: 可能因减少噪音而提升
- **实施优先级**: 数据预处理和调用频率控制快速见效

## 实施优先级

### P0（立即实施）
1. 数据预处理：技术指标替代原始数据
2. 调用频率控制：条件触发而非定时轮询
3. 输出格式约束：明确max_tokens限制

### P1（本周实施）
1. 提示词模板化
2. 请求合并（多币种分析）
3. 缓存机制实现

### P2（本月实施）
1. 动态参数调整
2. A/B测试框架
3. 自动化监控

## 监控指标
1. **token消耗**: 每日/每周总量，单次调用平均
2. **调用频率**: 成功调用 vs 被阻止调用
3. **缓存命中率**: 缓存有效减少的调用次数
4. **策略收益**: 优化前后的ROI对比
5. **响应时间**: 平均处理时间变化

## 注意事项
1. **质量底线**: 优化不能损伤决策质量
2. **逐步实施**: 先测试后推广
3. **持续监控**: 定期评估优化效果
4. **用户反馈**: 优先考虑用户体验

## 更新记录
- 2026-03-20: 创建文档，整合DeepSeek建议
- 2026-03-20: 分析当前系统状态，制定整合计划