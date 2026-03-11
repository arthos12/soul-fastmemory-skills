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

1. Search first
2. Rank by timeliness and criticality
3. Get only the needed snippets first
4. Reconstruct from the smallest useful context
5. Expand into deeper reads only when the information is important enough
6. Avoid broad scans and full-file loading unless necessary

Default restore order:

1. `LAST_SESSION.md`
2. `SESSION_HANDOFF.md`
3. `MEMORY.md`
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

This skill reduces session data loss by using two layers of persistence:

1. **Quick save path** for fast pre-reset protection
2. **Full handoff path** for proper session closure

If time is short, prefer quick save over doing nothing.

If the session appears likely to reset soon, prioritize writing the smallest high-value snapshot first.

## Read depth policy

Choose read depth based on retrieval value.

- **Shallow read** — use for low-criticality or archive checks
- **Standard read** — use for normal recent-context recovery
- **Deep read** — use for timely, critical, or decision-shaping information

Important information should not only be found first; it should also be read in greater detail.

## Writing rules

Every saved memory unit should prefer this order:

- Conclusion
- Next step
- Constraint or blocker
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
