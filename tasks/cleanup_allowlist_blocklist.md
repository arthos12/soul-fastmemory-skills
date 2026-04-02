# Cleanup Allowlist / Blocklist

## Goal
把垃圾治理从“凭感觉清理”改成“按白名单保护、按黑名单优先排查”。

## Allowlist — 默认保护对象
这些对象默认保留，不因整洁、压缩、提速理由直接删改：

### Brain core
- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `TASKS.md`
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `SELF_OPERATIONS.md`

### Skill core
- `skills/soul-booster/SKILL.md`
- `skills/soul-booster/references/brain_protection_and_hygiene_safety.md`
- `skills/soul-booster/references/core_runtime_rules.md`
- `skills/soul-booster/references/risk_predictive_execution.md`
- `skills/soul-booster/references/interaction_compression.md`
- `skills/soul-booster/references/context_budgeting.md`
- `skills/soul-booster/references/response_mode_budgeting.md`
- `skills/fast-memory/SKILL.md`
- `skills/fast-memory/references/memory_runtime_contract.md`
- `skills/fast-memory/references/training_state_restore_protocol.md`

### Recovery / continuity core
- `memory/YYYY-MM-DD.md`
- `tasks/*.md`
- 当前主线直接依赖的恢复/验收文档

## Blocklist — 优先排查对象
这些对象不是“立刻删除列表”，而是默认优先进入排查：

### Old recovery residue
- `memory/*-checkpoint.md`
- `NEW_SESSION_BOOT.md`
- 旧 handoff / 旧 boot / 重复恢复文本

### Bootstrap/template residue
- `BOOTSTRAP.md`
- `IDENTITY.md`（若仍为空模板）

### Build/install duplicates
- `dist/*`
- `skills-installed/*`
- `skills-active/*`（若与 `skills/*` 重复）

### Documentation bloat
- 阶段性 audit / retest / upgrade / result 文档长期堆积
- 同义重复规则文档
- 已被高层规则替代但仍单独残留的文档

### Code / reference redundancy
- 未被引用的脚本
- 未被挂接的 reference
- 重复实现、重复测试、重复说明文件

## Decision gate
Blocklist 对象要删除，仍需通过以下门槛：
1. 不属于大脑运行层
2. 不影响系统服务运行
3. 不影响恢复链路
4. 不影响当前 skill 生效
5. 已确认存在完整替代物，或确认根本无用

## Current first-batch candidates
- `memory/2026-03-11-checkpoint.md`
- `memory/2026-03-12-checkpoint.md`
- `BOOTSTRAP.md`
- `IDENTITY.md`
- `NEW_SESSION_BOOT.md`
- `dist/fast-memory.skill`
- `skills-installed/fast-memory.skill`
- `skills-active/fast-memory/*`（待确认是否为运行必需）
