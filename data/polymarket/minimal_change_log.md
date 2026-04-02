# minimal_change_log.md

规则：每个 batch 只允许新增 1 条“最小改动”。

## 2026-03-15 batch2
- 改动：把“预测样本生成”从手工口头变成脚本化流水线（pull -> predict -> score），确保空闲期至少能稳定产出 >=10 条结构化样本，并自动算出与市场概率差异指标。下一步改动只允许发生在 `polymarket_predict.py` 的预测逻辑（例如加入触发/失效与更合理先验）。
