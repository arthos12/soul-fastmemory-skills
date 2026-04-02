# 预设提示词模板

## 1. 策略报告解读
请用中文分析以下Polymarket策略指标：
- 订单总数：{orders}
- 胜率：{winrate}%
- ROI：{roi}%
- 浮盈/浮亏：{pnl}
- 选择率：{selection_rate}%

指出策略的主要优势和风险点，给出改进方向。

## 2. 参数优化建议
当前参数：
- minPrice: {minPrice}
- maxMinsToEnd: {maxMinsToEnd}
- keywords数量: {keyword_count}
- sizeUSD: {sizeUSD}

请推荐优化方向，解释每个参数变化的影响。

## 3. 问题诊断
当前问题：
- 问题1：{problem1}
- 问题2：{problem2}

请分析可能原因，给出解决方案。

## 4. 迭代总结
本次迭代：
- 变化：{changes}
- 效果：{effects}
- 下一步：{next_steps}

请总结经验，给出下一步建议。

---
## 使用方法
1. 填充{}中的变量
2. 发送给Minimax进行分析
3. 根据建议调整策略
4. 记录到ITERATION_TRACKER.md
