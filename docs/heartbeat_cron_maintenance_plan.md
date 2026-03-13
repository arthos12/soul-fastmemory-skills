# Heartbeat / Cron Maintenance Plan

## Goal
为“空闲时主动维护”补上可触发、低打扰、低 token 的执行方案；区分适合 heartbeat 的批处理检查，和适合 cron 的精确/独立任务。

## Principle
- heartbeat 用来做批量、低频、可漂移的维护
- cron 用来做精确、独立、可定时的动作
- 两者都要遵守：本地优先、低 token、短输出、不中断主线

## Heartbeat usage
适合 heartbeat 的事项：
1. 检查快恢复层是否缺失/过旧
2. 检查今天 memory 是否已建立
3. 检查 `TASKS.md` 当前主线是否有下一步
4. 做轻量 idle-action checklist
5. 检查最近是否有“已讨论但未保存”的关键需求

### Heartbeat rule
- 默认一次 heartbeat 只做 1-3 个小检查，不做全量审计
- 若无新增情况，直接保持静默/最小回复
- 若发现缺口，优先补文件，不先长解释

## Cron usage
适合 cron 的事项：
1. 小时级 session 保存提醒/自检
2. 每天固定时段检查今天 memory 是否存在
3. 每天/每几天做一次 memory 提纯或任务板整理
4. 对长期未推进的主线做一次低成本状态扫描

### Cron rule
- cron 任务必须足够短、独立、可恢复
- 不把大规模推理/重扫描放进 cron
- cron 输出以更新文件/短结果为主，不做长聊天式输出

## Recommended split
### Heartbeat
- 周期：有心跳就顺带做，不额外追求精确时间
- 内容：恢复层检查、主线下一步检查、今日 memory 存在性检查

### Cron
- 小时级：检查是否需要刷新 `LAST_SESSION.md` / `SESSION_HANDOFF.md`
- 每日级：检查 `memory/YYYY-MM-DD.md` 是否已创建
- 每 2-3 天：做一次 memory / TASKS 提纯与对齐检查

## Acceptance
方案达标需满足：
- 主线推进与恢复检查有固定触发层
- 不靠 Jim 每次手动提醒“去保存/去检查”
- 维护本身不变成高耗 token 行为
- heartbeat 与 cron 各自职责清楚，不混乱
