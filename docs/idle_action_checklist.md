# Idle Action Checklist

## Goal
把“空闲时主动推进”固定成可执行的小清单，避免空闲推进只停留在抽象原则层。

## Trigger
当满足以下条件时，可进入 idle mode：
- 当前没有新的高优先级用户消息
- 主线任务未完成
- 不涉及需要 Jim 立即拍板的安全/权限/资金/账号边界

## Default order
### 1. 先查主线
- 当前主线是什么？
- 当前步骤是什么？
- 下一步是否明确？
- 若不明确，先补 `LAST_SESSION.md` / `SESSION_HANDOFF.md` / `TASKS.md`

### 2. 先做低成本高价值动作
优先级从高到低：
1. 补快恢复层缺口
2. 补当天 `memory/YYYY-MM-DD.md`
3. 更新任务板 / 任务文件中的下一步
4. 做小范围覆盖检查 / 漏项回捞
5. 做本地优先的确定性检查
6. 整理能直接沉淀进 skill / docs 的稳定规则

### 3. 默认本地优先
优先使用：
- 本地文件读取/编辑
- 本地确定性检查
- 小范围 git / 状态检查
- 已有文档归集

避免：
- 为维护本身做高耗 token 大扫描
- 没必要的长推理与长输出
- 无边界地扩张并发

## Idle task buckets
### A. Recovery maintenance
- 检查 `LAST_SESSION.md` 是否存在且有 `Saved At`
- 检查 `SESSION_HANDOFF.md` 是否反映当前主线
- 检查今天的 `memory/YYYY-MM-DD.md` 是否存在

### B. Mainline progress
- 对照 `TASKS.md` 推进当前未完成主线
- 优先做能独立完成的小步动作
- 每完成一步就补下一步指针

### C. Capability upgrade
- 检查最近是否有“已理解但未执行 / 已讨论但未保存”的需求
- 把可复用规则下沉到 skill / docs
- 做小范围逻辑 / 理解 / 预判能力补强

### D. Risk check
- 检查是否存在会导致下次 `/new` 恢复失败的缺口
- 检查是否出现规则只写 daily log、未进快恢复层的问题
- 检查是否存在任务文件过期/状态不准

## Stop conditions
出现以下任一情况，立即退出 idle mode，回前台：
- Jim 发来新消息
- 触及必须确认边界
- 当前动作开始明显高负载/高风险
- 主线已被新的更高优先级任务替换

## Output rule
idle mode 默认不做长汇报；除非：
- 已完成一个清晰批次
- 发现关键 blocker / 风险
- Jim 明确要求看进度

## Pass standard
空闲推进结束后，至少满足一条：
- 主线前进一步
- 恢复链路更完整
- 关键规则真正落盘
- 下次 `/new` 更容易恢复
