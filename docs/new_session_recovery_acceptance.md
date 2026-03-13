# New Session Recovery Acceptance

## Goal
把“真实 `/new` + `加载数据` 验收”从口头要求变成可直接执行的固定验收流程，重点验证：主线恢复、行为恢复、能力恢复是否真的发生。

## When to run
- 每次 `/new` 后收到“加载数据 / 恢复数据 / 恢复记忆 / 先读一下”这类恢复指令时
- 每次改动 `LAST_SESSION.md` / `SESSION_HANDOFF.md` / `TASKS.md` / fast-memory 恢复策略后
- 每次怀疑“session 切换后能力波动”时

## Restore input priority
1. `LAST_SESSION.md`
2. `SESSION_HANDOFF.md`
3. `TASKS.md`
4. `memory/YYYY-MM-DD.md`（今天优先，没有则读昨天并补建今天）
5. 必要时再读 `MEMORY.md` / 对应任务文件

## Required recovery output
恢复后，前台必须能在短回复中直接说清：
- 最近一次 `Saved At`
- 当前主线
- 当前步骤
- 下一步
- 当前 blocker / 缺口
- 当前运行模式（默认 light；复杂场景再升 mid/heavy）

## Acceptance checks

### A. Mainline recovery
- 能否直接说清当前主线，而不是泛泛总结历史
- 能否给出当前步骤与紧接着的下一步
- 能否指出未完成项，而不是误报“都已完成”

### B. Behavior recovery
- 是否仍按“任务推进模式”工作，而不是退回纯问答/纯解释
- 是否保留“回复后恢复主线”的默认行为
- 是否在需要时先短答状态，再继续后台推进

### C. Capability recovery
- 是否恢复以下能力与约束：
  - 空闲推进主线
  - 本地优先维护
  - 碎片化需求处理
  - token 优化 / 轻量回复预算
  - 自我检查未执行 / 未保存需求

## Failure patterns
若出现以下任一情况，视为恢复未达标：
- 只读 daily log，不读快恢复层
- 只能说历史背景，不能说当前主线/当前步骤
- 重新变成逐句被动问答，不继续主线推进
- 恢复后忘记本轮新增运行策略（如 token 优化、本地优先、空闲推进）
- 今天的 memory 缺失却未主动补建

## Repair actions when failed
1. 立即补建/更新 `memory/YYYY-MM-DD.md`
2. 刷新 `LAST_SESSION.md` / `SESSION_HANDOFF.md`
3. 必要时更新 `TASKS.md` 与任务文件
4. 记录失败类型：mainline / behavior / capability
5. 把修复结果重新写入快恢复层，等待下一次真实 `/new` 再验

## Pass standard
一次真实 `/new` + `加载数据` 后，能在低互动条件下：
- 直接恢复当前主线与下一步
- 保持任务推进模式
- 恢复关键运行能力与约束
- 不依赖用户再次重新解释背景
