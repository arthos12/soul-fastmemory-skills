# Workspace Hygiene & Speed Task

## Goal
低频维护式地清理垃圾文件、垃圾代码、重复产物、无效 checkpoint、过期模板和冗余流程，降低工作区复杂度，提升系统速度、恢复速度、响应速度与维护稳定性；核心目的不是整洁本身，而是避免垃圾持续浪费系统存储空间，并减少无效文件/代码/流程对内存、CPU、检索与恢复链路的占用。

## Priority rule
这是低频、低优先级维护项：很久做一次，不高频做；默认不能抢占高频需求、主线任务推进、能力训练与恢复验收的注意力。只有在明显影响速度、恢复、存储或运行时，才允许插队处理。

## Why this task exists
Jim 明确要求：不要有很多垃圾文件造成系统冗余；没用的文件应删除；同时要从源头上持续寻找“垃圾的来源”，而不是只做一次性清理。

## Core principle
- 大脑保护优先于一切清理动作
- 少文件
- 少重复
- 少无效中间产物
- 少过期规则/死代码
- 保留恢复链路所必需的最小集合
- 性能优先，不为整洁而整洁
- 优先清理会浪费磁盘、拖慢检索/恢复、增加 CPU/内存负担的垃圾

## Highest constraint
任何清理、删改、提纯、合并动作，都必须先服从以下硬约束：
1. **最优先保护大脑运行层**，不能做会损害大脑运行的改动。
2. **不能破坏系统服务运行**，不能因删除文件/数据导致服务、skill、恢复链路、任务推进失效。
3. **不能破坏恢复链路**，宁可暂时保留冗余，也不允许把恢复能力删残。

这里的“大脑运行层”至少包括：
- `SOUL.md`
- `MEMORY.md`
- `USER.md`
- `TASKS.md`
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `SELF_OPERATIONS.md`
- 当前实际被运行链路使用的 `skills/soul-booster/*`
- 当前实际被运行链路使用的 `skills/fast-memory/*`
- 以及它们依赖的恢复/规则/引用文件

## Performance objective
以后判断“是不是垃圾”，优先看它是否造成以下问题：
1. 浪费磁盘空间
2. 增加文件扫描/检索/恢复负担
3. 让系统做重复判断、重复加载、重复维护
4. 造成不必要的 CPU / 内存 / 上下文开销
5. 继续制造新的冗余文件、冗余代码、冗余流程

## Garbage source categories
### 1. 恢复层冗余
- 多余 checkpoint
- 过期 handoff / boot / 初始化遗留文件
- daily memory 之外的重复恢复文本

### 2. 构建/安装重复产物
- `dist/*`
- `skills-installed/*`
- `skills-active/*`
- 与源 skill 重复、但不再被当前运行链路实际依赖的副本

### 3. 文档与规则冗余
- 相同意思被多份文档重复记录
- 已被更高层规则替代，但旧文件仍保留
- 只产生噪音、无法帮助恢复/执行/验收的文档

### 4. 代码/逻辑冗余
- 已不再被引用的脚本/规则
- 与当前主线无关、但残留在 skill 中的逻辑
- 明显重复实现的代码或测试文件

### 5. 流程冗余
- 可以直接覆盖更新，却不断另存新文件
- 可以合并的检查，却拆成太多碎文件
- 低价值保存动作导致恢复链路膨胀

## Default cleanup order
1. 先删低风险垃圾：无用 checkpoint、临时/构建重复产物、初始化遗留模板
2. 再做文档提纯：合并重复规则、移除被替代文档
3. 再做代码/skill 冗余清理：删掉未引用/重复/过期逻辑
4. 最后做流程优化：减少未来继续产垃圾的机制

## Sync policy around training
- 默认顺序：先训练 / 先长脑子，再在空闲时做 skill 同步。
- skill 同步不是每次本地变化后立刻强制执行，但不能长期失配。
- 同步前必须检查：是否会丢需求、丢功能、降能力、削弱恢复或破坏运行边界。
- 若同步存在保真风险，优先保留本地运行版本，等可安全迁移时再同步。

## Keep rules
以下默认保留：
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `TASKS.md`
- `MEMORY.md`
- `memory/YYYY-MM-DD.md`
- 当前仍被引用的核心 docs / skill references

## Delete rules
满足以下条件可删：
- 不再被当前运行链路使用
- 不影响恢复、执行、验收
- 与现存文件重复，且现存文件更完整
- 属于一次性中间产物/构建产物/过期模板

## Future anti-garbage policy
以后发现垃圾时，不只删除，还要追根到来源：
- 为什么会生成这个文件/代码？
- 是哪个流程默认在制造它？
- 应否改为覆盖、合并、或不生成？

## Current first batch suspects
- `memory/2026-03-11-checkpoint.md`
- `memory/2026-03-12-checkpoint.md`
- `dist/fast-memory.skill`
- `skills-installed/fast-memory.skill`
- `BOOTSTRAP.md`
- `NEW_SESSION_BOOT.md`
- 可能重复的 `skills-active/fast-memory/*`

## Supporting task files
- `tasks/runtime_dependency_map.md`
- `tasks/cleanup_allowlist_blocklist.md`
- `tasks/skill_sync_gap_list.md`

## Done when
- 已建立稳定的垃圾来源分类法
- 已完成至少一轮低风险清理
- 已把“找垃圾来源”变成持续任务，而不是临时动作
