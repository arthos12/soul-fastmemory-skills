---
name: fast-memory
description: "Installable structured memory skill for OpenClaw agents. Use for fast session restore, layered memory writing, quick-save handoff, recent full-session fallback, multi-stage retention, and compact long-term memory management."
---

<!-- Author: jim -->

# Fast Memory

## 定位
这个 skill 承载的是当前记忆系统的主要工作方式，不只是“能写记忆”，而是把分层存储、按需检索、session 恢复、收尾落盘、防污染提速这整套机制迁移给其他 bot / agent。

## 对外迁移目标
当其他 bot / agent 安装这个 skill 时，目标不是只学会如何保存几条笔记，而是尽量学到当前这套记忆系统的分层结构、查询路径、写入原则、恢复机制、收尾机制与防污染策略。

默认记忆运行接管规范见 [references/memory_runtime_contract.md](references/memory_runtime_contract.md)。
硬约束规则见 [references/enforcement_rules.md](references/enforcement_rules.md)。
安装后的行为验收见 [references/behavior_tests.md](references/behavior_tests.md)。
真实任务测试集见 [references/test_tasks.md](references/test_tasks.md)。

Use this skill when the agent needs a practical memory system that can be applied immediately after installation.

## What this skill does

This skill tells the agent how to:

1. restore recent work quickly in a new session
2. classify content before saving
3. save high-value logic more completely
4. keep recent full sessions as a short-term fallback buffer
5. move older sessions into extracted structured storage
6. downgrade colder content when storage becomes too large

Core principle:

> Understand logic first. Classify second. Save by importance and retrieval value.

## Default operating model

Use a layered memory model with four active parts:

1. **Long-term stable memory**
   - file: `MEMORY.md`
   - stores durable rules, stable preferences, recurring principles, important long-term logic

2. **Structured near-term memory**
   - files: `LAST_SESSION.md`, `SESSION_HANDOFF.md`, relevant project checkpoints
   - stores the recent main line, current step, goal, next action, blockers, key files

3. **Recent full-session buffer**
   - keep the most recent **3** full sessions by default
   - in constrained environments, keep **1**
   - use only as a fallback when structured memory is insufficient

4. **Downgrade / cleanup layer**
   - when extracted storage grows too large, compress colder content into a more compact second-pass layer
   - remove old raw sessions only after important logic has been transferred

## Default execution parameters

Use these defaults unless the user explicitly changes them:

- recent full-session buffer: **3 sessions**
- constrained mode buffer: **1 session**
- hot retention window: **3 days**
- restore priority: **structured memory first, full-session fallback second**
- save rule: **higher importance = higher completeness**

Treat extracted storage as too large when any of these become true:
- reading it is no longer fast
- the same topic has accumulated too much structure
- cold / rarely used content is taking a large share

Treat content as cold / downgrade-ready when most of these are true:
- rarely used
- outside the current main work line
- lower importance level
- not recently asked about
- low recovery value for current work

## Retrieval rules

At new-session restore time, run this sequence:

1. load recent structured content first
2. identify important content inside the recent content
3. find the most important content and the recently important content
4. understand:
   - topic / 事情名称
   - logic / 事情逻辑
   - short description / 简要描述
   - current step / 当前步骤
   - goal / 目标
5. add:
   - key information / 关键信息
   - fuller related information / 全面信息
   - accurate details / 准确信息
   - relevant files
6. if structured memory is insufficient, fall back to the recent full-session buffer
7. reconstruct the working state compactly

Default restore order:
1. `LAST_SESSION.md`
2. `SESSION_HANDOFF.md`
3. `MEMORY.md`
4. recent daily notes
5. project checkpoints
6. recent full-session buffer if needed

## Saving rules

Before saving, classify the content:

- 长期规则
- 最近会话内容
- 交接内容
- 当天细节
- 项目进度
- 临时噪音

Then assign one of six importance levels:

1. 第1层 — 核心逻辑、核心目标、核心工作流主线
2. 第2层 — 关键步骤、关键结论、关键决策、关键约束
3. 第3层 — 关键数据、关键文件、关键上下文、关键关联信息
4. 第4层 — 一般工作细节、阶段性信息、普通背景
5. 第5层 — 低复用描述、普通背景、低价值补充
6. 第6层 — 临时噪音、无后续价值内容

Save by importance:

- 第1-2层 → 完整保存
- 第3层 → 重点保存
- 第4-5层 → 压缩保存
- 第6层 → 不保存

Prefer this field order when saving:

- 事情名称
- 事情逻辑
- 简要描述
- 当前步骤
- 目标
- 关键信息
- relevant files
- next action / blocker when needed

## Storage destinations

- `MEMORY.md`
  - durable rules, stable logic, long-term preferences

- `LAST_SESSION.md`
  - recent main line, high-value recent context, recent important work

- `SESSION_HANDOFF.md`
  - next step, blockers, current state, quick-save protection

- `memory/YYYY-MM-DD.md`
  - same-day detail, medium-value notes, process residue

- project checkpoints
  - multi-session project state, risks, stage, next step

- recent full-session buffer
  - raw fallback only

## Lifecycle rules

Use three storage states:

### 1. Recent session: full preservation
Keep recent sessions fully preserved as hot data.

### 2. After 3 days: extracted transfer
Move high-value content from older sessions into structured extracted storage.

Transfer at least:
- 事情名称
- 事情逻辑
- 当前步骤
- 目标
- 关键信息
- 关键文件
- 关键结论
- 下一步 / 阻塞

### 3. If storage grows too large: second-pass extraction
Downgrade colder / lower-priority content into a more compressed layer.

Rule:
- high-value main-line logic stays richer
- colder and lower-frequency content gets compressed more
- low-value residue can be removed later

## Old-session cleanup rule

Do not delete old raw sessions until high-value information has been transferred.

Delete raw old sessions only when all are true:
- core logic has been extracted
- key content has been moved into structured memory
- the session has gone unused long enough
- recovery value is now low

Rule:

> Delete raw history, not high-value memory.

## Dynamic save (incremental session saving)

**Default: dynamic save without being asked.** Do not wait for an explicit “结束 session / 保存一下” command.
**Also default-save at least once every ~1 hour of active session time, even if the user does not remind you.**
**And before `/new`, treat saving the current session as mandatory, not optional.**

Goal: make `/new`-resets harmless by keeping a rolling, incremental snapshot of the current work.

### Triggers (3 tiers)

1) **Hard triggers (save immediately)**
- the user confirms a decision / conclusion (“就这么定 / 按这个做”)
- any key parameters appear: lists, links, file names/paths, configs/tokens, exact values
- next-step / blocker changes
- high reset risk: user likely to hit `/new`, model/tool instability, long pause, topic switch

2) **Soft triggers (periodic incremental saves)**
- the topic stays the same and information is clearly accumulating across multiple turns
- the agent outputs an actionable plan/template/checklist worth reusing

Default soft cadence (unless user changes it): **every 10–15 turns**, or **each completed sub-point** (conservative, to reduce server workload).

3) **Closure triggers (stage completed)**
- a sub-task is finished (e.g., “skill updated + repacked + verified”)

### Write targets (2 layers)

- **`SESSION_HANDOFF.md` = fast rolling snapshot** (lightweight, frequent)
  - current topic
  - latest confirmed conclusion
  - next step
  - blocker/constraint
  - relevant files/links

- **`LAST_SESSION.md` = fast-recovery main line** (denser, but still compact)
  - refresh in the same pass when the main line is clear and recovery value is high

Minimum fields for a dynamic save entry:
- 事情名称
- 简要描述
- 当前步骤
- 下一步
- 阻塞/约束（如有）
- relevant files

## Quick-save rule

When time is short or a reset is likely, save quickly into `SESSION_HANDOFF.md`.

Minimum quick-save content:
- current topic
- confirmed conclusion
- next step
- blocker or constraint
- relevant files
- if self-training/acceptance is ongoing: current capability level, remaining weaknesses, next upgrade target
- if understanding failed: exact misread pattern (e.g. missed main question / failed to split compound question / followed keywords instead of intent)

If any of these are true, also refresh `LAST_SESSION.md` in the same save pass:
- the current main line is already clear
- the user is likely to continue this work soon
- the recent near-term context has high recovery value
- the user is ending the round, asking to save, or a reset is likely

Rule:

> `LAST_SESSION.md` is the default fast-recovery layer for the recent main line, not an optional extra.

## Full-handoff rule

When closing a work round more cleanly, update:
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- daily note if needed
- `MEMORY.md` if durable logic should be promoted

If `LAST_SESSION.md` is missing after a meaningful work round, treat the save loop as incomplete and refresh it before considering the handoff finished.

## Stall-risk / freeze-protection rule

If the agent detects a meaningful risk of stalling, hanging, or becoming unresponsive before replying, it must write a compact diagnostic note into retrievable memory **before** continuing or failing.

Minimum diagnostic fields:
- current topic
- user trigger / last user ask
- last completed step
- current blocked step
- suspected cause
- relevant files / tools if any

Default write target:
- `memory/YYYY-MM-DD.md`

Also refresh at least one fast-recovery layer when recovery value is high:
- `SESSION_HANDOFF.md`
- `LAST_SESSION.md`

Response rule:
- do not let long checks fully block the first visible reply
- when stall risk is detected, prefer a short immediate user-facing status reply first, then continue the deeper check

Goal:
- make freezes diagnosable
- preserve the last good state
- reduce the chance that a silent stall destroys recoverability

## Anti-pollution rules

Do not bloat long-term memory.

Always:
- separate durable rules from same-day detail
- compress before writing long narrative logs
- merge duplicates instead of re-saving paraphrases
- keep `MEMORY.md` thin
- keep `LAST_SESSION.md` richer than `MEMORY.md`

## Templates and references

If needed, read:
- `references/templates.md`
- `references/strategy.md`
- `references/需求文档.md`

If the user wants to change the system logic, update `references/需求文档.md` first, then bring the skill into sync.
