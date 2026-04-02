# Capability Persistence And Recovery

## Core rule
所有已经形成并验证有效的大脑能力、理解能力、思考能力、逻辑能力、恢复能力与关键运行规则，不能只存在当前 session / 当前 API 上下文中。
必须进入可恢复层，确保 session 断了、API 断了之后，这些能力和大脑不会消失。

## What must persist
包括但不限于：
- 理解能力相关规则
- 思考 / 逻辑推理 / 判断 / 决策规则
- 重要执行流程
- 停止条件
- 自我进化护栏
- 高质量落盘规则
- 回读修改闭环
- 恢复流程与恢复锚点
- 训练 Bot 的核心架构

## Persistence targets
这些能力至少应进入以下一处或多处：
- `skills/soul-booster/` 对应 rule / reference 文件
- `MEMORY.md`
- `TASKS.md`
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `memory/YYYY-MM-DD.md`（保留形成过程与当天变更）

## Recovery requirement
当 session 断开、API 中断、重新开始时，默认必须能够通过读取规则层、长期记忆层、任务层和交接层，恢复：
- 当前主脑规则
- 当前主线任务
- 当前有效能力结构
- 最近关键升级与变更
- 下一步指针

## Principle
能力真正生效，不以“我刚刚说过”为准，而以“是否已经进入可恢复层，能否在断点后重新加载恢复”为准。

## Summary
不能把能力存在聊天里。
能力要写进可恢复系统里，断了也能回来。
