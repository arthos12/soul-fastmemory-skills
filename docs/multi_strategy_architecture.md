# Multi-Strategy Architecture (v1)

目标：支持多条策略并行运行，每条策略独立产出样本、结果、收益和风险摘要；后续可同时覆盖：
- PM 预测量化
- 交易所短周期量化

## 当前已落地
- `strategies/strategy_registry.json`：统一策略注册表
- `scripts/multi_strategy_runner.py`：按 registry 批量跑策略
- 每条策略保留独立 `id/kind/tag/strategyVersion`
- 统一 dashboard 输出：`data/strategy_hub/latest_run.json`

## 当前 kind
- `pm_paper`: 已接入真实 runner（调用 `scripts/pm_paper_loop.py`）
- `cex_paper`: 先保留占位 summary，下一步接入真实交易所 paper runner

## 每条策略的最小验收字段
- strategy id
- strategy kind
- strategy version
- sample size
- realized_n / m2m_n
- realized winrate
- realized roi avg
- m2m roi avg
- pnl sum
- max drawdown proxy
- fee / slippage assumptions（cex）

## 下一步
1. 接入 `cex_paper_loop.py`
2. 统一 order/result schema
3. 引入每策略手续费/滑点净收益统计
4. 加总览排名：按样本量、净收益、回撤、稳定性排序
