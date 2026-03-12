---
name: fast-memory
description: "Fast structured memory system for OpenClaw-style agents. Use when creating or improving memory workflows, session restore behavior, quick-save handoff logic, long-term memory hygiene, checkpoint logging, retrieval-speed optimization, or crash-resistant session continuity. Also use when an agent needs a reusable method for automatic restore on new sessions, quick save before resets, search-then-get retrieval, and high-signal memory writing rules." 
---

<!-- Author: jim -->

# Fast Memory

Use this skill to make agent memory faster, cleaner, more stable, and more selective across sessions.

## Minimal core rules

1. Understand the logic first.
2. Save only what matters.
3. Preserve important information more completely.
4. Retrieve recent, critical, and frequently used information first.
5. Let old, low-value, rarely used information decay.

## Core objective

North star:

> Do not lose important memory. Load recent memory fast. Handle large working data without forgetting what matters.

Optimize for four outcomes at the same time:

1. Faster memory restore
2. Higher signal retention
3. Lower session-data loss risk
4. Better handling of large working data without burying key information

Do not try to capture everything or process everything.
Focus on the smallest set of information that preserves continuity, logic, and next action.

Treat memory as a layered persistence system, not as implicit chat recall.

Use this storage rule:

> Classify first. Rank second. Store by retrieval priority.

## Importance judgment

Use this importance order:

1. Logic weight
2. Theme value
3. Repetition and reinforcement by the user
4. Workflow relevance
5. Timeliness
6. Criticality
7. Retrieval probability

Repeated, logic-heavy user themes should be treated as top-tier memory.

## Classification and priority

Before writing memory, classify the data first:

- long-term rule
- last-session context
- handoff action
- daily detail
- project checkpoint
- temporary noise

Then assign a priority level:

- `P0` — critical, must restore fast
- `P1` — important, likely needed soon
- `P2` — useful, but not immediate
- `P3` — archive only

Then evaluate timeliness:

- `Immediate` — likely needed in the next session
- `Near-term` — likely needed in the next few sessions
- `Mid-term` — useful during ongoing project work
- `Long-term` — durable and stable over time
- `Archive` — mostly historical

Then evaluate criticality:

- `C0` — mission critical
- `C1` — highly important
- `C2` — useful
- `C3` — background only

Then store by retrieval lane:

- **Fast lane** — `LAST_SESSION.md`, `SESSION_HANDOFF.md`
- **Stable lane** — `MEMORY.md`
- **Archive lane** — daily notes and project checkpoints

Not all memory deserves the same retrieval speed.

Timely and critical information should be retrieved first and read more deeply.

## Memory layers

Use these layers with strict separation:

- `LAST_SESSION.md` — high-priority snapshot of the most recent session, with richer near-term recovery data
- `SESSION_HANDOFF.md` — current recovery state, quick-save snapshot, next actions
- `MEMORY.md` — long-term rules, stable preferences, durable constraints, key paths
- `memory/YYYY-MM-DD.md` — daily conclusions, recent task state, short-lived notes
- Project checkpoint files — multi-session work with deeper task continuity

Do not mix durable rules with same-day noise.

Keep this design rule in mind:

- long-term memory should stay thin
- last-session memory should stay rich

## Retrieval logic

Always use targeted retrieval.

1. Load recent content first
2. Identify the important content inside the recent content
3. Find the most important content and the recently important content
4. Understand what the user is doing before expanding detail
5. Search first
6. Rank by timeliness and criticality
7. Get only the needed snippets first
8. Reconstruct from the smallest useful context
9. Expand into deeper reads only when the information is important enough
10. Avoid broad scans and full-file loading unless necessary

When restoring context, first understand:
- what the user is doing
- the logic of the work
- the current step
- the overall goal

Prefer structured memory first.
If structured memory is insufficient, fall back to the recent full-session buffer.

Then expand by logic to capture:
- key information
- fuller related information
- accurate details

Default restore order:

1. The most recent and most important work (`LAST_SESSION.md`)
2. Current handoff and next-action state (`SESSION_HANDOFF.md`)
3. Stable long-term rules (`MEMORY.md`)
4. Recent daily notes
5. Relevant project checkpoints

## Session continuity logic

### Automatic restore

At the start of a new session, restore memory automatically when the workspace supports it, even if the user does not know the exact trigger phrase.

Minimum restore set:

1. Last-session snapshot
2. Current handoff
3. Long-term memory
4. Recent daily notes

Then summarize only:

- active topic
- latest confirmed conclusions
- next action
- blockers or constraints

When a retrieved item is both timely and critical, prefer a deeper read before final reconstruction.

### Quick save

Use quick save before a likely reset, handoff, or session switch.

Quick save is the default lightweight protection path and should be preferred when speed matters.

Store only:

- current topic
- confirmed conclusion
- next step
- blocker or constraint
- relevant file(s)

Write quick save into `SESSION_HANDOFF.md`. When the most recent session contains especially high-value near-term context, also refresh `LAST_SESSION.md`. Optionally append one compact line to the daily note if needed.

### Full handoff

Use full handoff when the user is clearly ending the working round.

Store:

- conclusion set
- recent key discussion points
- next-step set
- blockers
- relevant files
- durable rules worth promotion

Write to:

- `LAST_SESSION.md` for richer recent-session recovery
- daily notes
- session handoff
- long-term memory when durable

## Anti-pollution and speed policy

Use six mandatory gates:

1. **Layering gate** — keep durable rules, daily detail, and handoff state separate
2. **Compression gate** — write conclusions, next steps, constraints; avoid narrative logs
3. **Cleanup gate** — merge duplicates, mark stale items, move durable rules upward
4. **Admission gate** — only store long-term-useful or decision-relevant information in `MEMORY.md`
5. **Deduplication gate** — update old rules instead of adding paraphrased duplicates
6. **Expiration gate** — keep temporary and phase-specific information out of long-term memory unless explicitly labeled

Core principle: anti-pollution is a speed system.

## Data-loss reduction logic

This skill reduces session data loss by using multiple layers of persistence:

1. **Quick save path** for fast pre-reset protection
2. **Full handoff path** for proper session closure
3. **Recent full-session buffer** for short-term raw context fallback

If time is short, prefer quick save over doing nothing.

If the session appears likely to reset soon, prioritize writing the smallest high-value snapshot first.

Retain the most recent sessions as a short-term raw buffer when possible.
Use structured memory for speed first, and fall back to full-session history only when important details were not sufficiently preserved.

Use this lifecycle:
1. recent sessions stay fully preserved as hot data
2. after roughly 3 days, move the high-value content into extracted structured storage
3. if extracted storage becomes too large, demote colder / lower-priority content into a second-pass compressed layer

Do not keep old full-session buffers forever: remove them only after the core logic has been extracted and the session has gone unused long enough.

## Read depth policy

Choose read depth based on retrieval value.

- **Shallow read** — use for low-criticality or archive checks
- **Standard read** — use for normal recent-context recovery
- **Deep read** — use for timely, critical, or decision-shaping information

Important information should not only be found first; it should also be read in greater detail.

## Content classification and storage rules

Classify content by what role it plays in the work:

- **长期规则** — durable methods, stable preferences, recurring principles
- **最近会话内容** — recent work likely to continue soon
- **交接内容** — next actions, blockers, state needed for continuation
- **当天细节** — same-day process detail and minor conclusions
- **项目进度** — multi-session work state, phase, risks, next step
- **临时噪音** — low-value chatter, one-off fragments, irrelevant detail

Use six importance levels:

1. **第1层** — 核心逻辑、核心目标、核心工作流主线
2. **第2层** — 关键步骤、关键结论、关键决策、关键约束
3. **第3层** — 关键数据、关键文件、关键上下文、关键关联信息
4. **第4层** — 一般工作细节、阶段性信息、普通背景
5. **第5层** — 低复用描述、普通背景、低价值补充
6. **第6层** — 临时噪音、无后续价值内容

Store by role and importance:

- `MEMORY.md` — 长期规则，尤其是第1-2层的稳定逻辑
- `LAST_SESSION.md` — 最近会话内容里第1-3层的高价值部分
- `SESSION_HANDOFF.md` — 交接内容，尤其是下一步、阻塞、当前状态
- `memory/YYYY-MM-DD.md` — 当天细节、第3-5层的一般工作信息
- project checkpoints — 项目进度、多轮推进状态、相关风险和下一步
- skip — 第6层内容，以及明显不值得保留的低价值噪音

Store with different completeness levels:

- **完整保存** — 第1-2层，保留逻辑、主题、步骤、目标、关键细节
- **重点保存** — 第3层，保留关键数据、关键文件、关键上下文
- **压缩保存** — 第4-5层，只保留必要结论和少量残留
- **不保存** — 第6层

Every saved memory unit should prefer this order:

- 事情名称 / Topic
- 事情逻辑 / Logic
- 简要描述 / Description
- 当前步骤 / Current step
- 目标 / Goal
- 关键信息 / Key information
- Relevant files

Avoid saving:

- long dialogue transcripts
- repeated paraphrases
- low-value chatter
- unstable short-term noise in long-term memory

## Maintenance cycle

Run light maintenance periodically:

- merge duplicate long-term rules
- remove or mark expired items
- promote durable patterns from recent notes
- keep `MEMORY.md` compact enough to stay fast

## Templates

If reusable save formats are needed, read `references/templates.md`.
If a fuller strategy document is needed, read `references/strategy.md`.
If the full product logic / requirements need to be reviewed or updated before changing the skill, read `references/需求文档.md` first.
