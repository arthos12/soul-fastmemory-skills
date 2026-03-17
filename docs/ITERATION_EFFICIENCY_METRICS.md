# Iteration Efficiency Metrics (迭代效率指标)

目的：把“主动/时间观念/效率观念”落成可计数指标，避免有安排但不执行。

## What counts as one iteration
任意满足其一即可计为 1 次迭代：
- 策略参数改动（strategies/*.json 变更）并跑出新订单
- 新增一批 paper_orders（>=1条）
- 新增一批 paper_results 回填（>=1条）
- 新增一份 hourly_report（含订单/回填/ROI字段）
- 脚本修复并通过最小自测（能产出/能回填/能报告）

## Minimum cadence
- 每小时迭代次数 >= 1
- 短周期任务：10分钟内必须有回填检查动作（无结果也要产出“检查证据”）

## Failure triggers
- 连续2小时迭代次数=0
- 订单=0 持续
- 回填=0 持续

触发后必须：
- 立刻停聊天 → 下钻修卡点 → 换路 → 直到恢复迭代产出
