# BR Always-On 主线任务

目标：BR 预测/下单测试必须持续运行，不能被聊天、复盘、规则整理打断。

## 硬要求
- 持续下单测试：默认每 10 分钟一轮
- 持续回填检查：每轮都要产出 results/report
- 持续状态监督：记录 last_run / last_orders / last_results / status
- 若连续 2 轮 orders=0 或 results=0，立即视为故障并切到修复优先

## 当前验收
- `data/polymarket/runtime/br_loop_status.json` 持续更新
- 后台 loop 持续运行
- 聊天进行中也不能停止主线
