# Runtime Dependency Map

## Goal
给后续垃圾治理、文档提纯、skill 同步、低风险清理提供最小运行依赖图，避免靠感觉删文件，导致大脑、服务、恢复链路受损。

## Layer 0 — 核心运行层（默认禁止清理）
这些文件/目录默认视为大脑与运行主链的一部分，未确认替代链路前禁止删除或合并：

### Workspace core
- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `TASKS.md`
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `SELF_OPERATIONS.md`

### Brain / memory core skills
- `skills/soul-booster/SKILL.md`
- `skills/soul-booster/references/*`（按实际引用链优先保留）
- `skills/fast-memory/SKILL.md`
- `skills/fast-memory/references/*`（按实际引用链优先保留）

## Layer 1 — 快恢复 / 任务支持层（谨慎清理）
这些对象不一定 100% 核心运行，但直接影响恢复、任务连续性和工作状态重建：
- `memory/YYYY-MM-DD.md`
- `tasks/*.md`
- `docs/new_session_recovery_acceptance.md`
- `docs/session_restore_recovery_plan.md`
- `docs/token_optimization_strategy.md`
- 与当前主线直接相关的验收/协议/审计文档

## Layer 2 — 阶段性支持层（可提纯）
这些对象通常用于阶段性训练、测试、审计、升级回顾；可保留，但后续可以合并或提纯：
- `docs/*audit*`
- `docs/*retest*`
- `docs/*upgrade*`
- `docs/*plan*`
- 训练阶段结果文档

## Layer 3 — 可疑冗余层（优先排查）
这层是垃圾治理任务的重点来源，但仍需先做依赖判断：
- `memory/*-checkpoint.md`
- `BOOTSTRAP.md`
- `IDENTITY.md`
- `NEW_SESSION_BOOT.md`
- `dist/*`
- `skills-installed/*`
- `skills-active/*`（若与源 skill 重复且不再被实际依赖）
- 未引用脚本/未引用 reference/重复产物

## Cleanup routing rule
以后每个候选垃圾都先放到这张图里分层：
1. 若属于 Layer 0 → 默认不动
2. 若属于 Layer 1 → 仅在已确认替代链路后再动
3. 若属于 Layer 2 → 优先考虑合并/提纯，不急删
4. 若属于 Layer 3 → 进入优先排查清单

## Current note
当前已知最需要优先保护的是：
- 大脑运行层
- 系统服务运行
- session 恢复链路
- soul / fast-memory 的实际生效链路

所以后续清理默认先从 Layer 3 开始，而不是碰核心层。
