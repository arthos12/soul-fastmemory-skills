<!-- Author: jim -->

# Fast Memory Strategy

## Minimal core rules

1. Understand the logic first.
2. Save only what matters.
3. Preserve important information more completely.
4. Retrieve recent, critical, and frequently used information first.
5. Let old, low-value, rarely used information decay.

## Goal

Build a memory workflow that does not lose important memory, restores recent memory fast, and handles large working data without forgetting what matters.

## Design priorities

1. Speed first
2. Stability second
3. High-signal retention
4. Minimal memory pollution
5. Better session continuity
6. Lower write cost for routine saves
7. Better scaling under large working data

Do not capture everything.
Capture the smallest amount of information that preserves logic, continuity, and execution quality.

## Classification and priority model

Classify first, rank second, and then store by retrieval priority.

### Classification
Classify each memory unit as one of:
- long-term rule
- last-session context
- handoff action
- daily detail
- project checkpoint
- temporary noise

### Priority levels
Assign one of these levels:
- `P0` — critical, must restore fast
- `P1` — important, likely needed soon
- `P2` — useful, but not immediate
- `P3` — archive only

### Timeliness
Estimate when the information will likely be needed:
- `Immediate`
- `Near-term`
- `Mid-term`
- `Long-term`
- `Archive`

### Criticality
Estimate how important the information is:
- `C0` — mission critical
- `C1` — highly important
- `C2` — useful
- `C3` — background only

### Storage lanes
Store by retrieval speed:
- **Fast lane** — `LAST_SESSION.md`, `SESSION_HANDOFF.md`
- **Stable lane** — `MEMORY.md`
- **Archive lane** — daily notes, project checkpoints

This means memory is not only layered; it is also prioritized.

## Layer model

### Last-session layer
Use `LAST_SESSION.md` for the richest high-priority snapshot of the most recent session. This layer should preserve near-term context that is highly likely to matter in the next session.

### Handoff layer
Use `SESSION_HANDOFF.md` for the latest compact recovery snapshot.

### Long-term layer
Use `MEMORY.md` for durable rules, stable preferences, important constraints, and key paths.

### Daily layer
Use `memory/YYYY-MM-DD.md` for recent conclusions, short-lived notes, and same-day task state.

### Project layer
Use dedicated checkpoint files for complex multi-session work.

## Restore model

### Standard restore
Load in this order:
1. the most recent and most important work (`LAST_SESSION.md`)
2. current handoff and next-action state (`SESSION_HANDOFF.md`)
3. stable long-term rules (`MEMORY.md`)
4. recent daily notes
5. relevant checkpoints

### Restore understanding target
Before reconstructing the session, understand:
- what the user is doing
- the logic of the work
- the current step
- the overall goal

Then use logic to expand into:
- key information
- fuller related information
- accurate details

### Restore output
Only rebuild:
- current topic
- confirmed decisions
- next step
- blockers
- relevant files

If an item is both highly timely and highly critical, read more deeply before final reconstruction.

## Save model

### Classification and storage decision
When saving content, decide in this order:
1. what kind of content it is
2. which of the 6 importance levels it belongs to
3. where it should be stored
4. how completely it should be stored

### Quick save
Use when speed matters or a reset is likely.

Save only:
- 事情名称 / topic
- 事情逻辑 / logic
- current step
- goal
- conclusion
- next step
- blocker or constraint
- relevant files

When the latest session contains especially important near-term state, also refresh `LAST_SESSION.md` so that the newest context gets highest retrieval priority.

### Full handoff
Use when ending a working round cleanly.

Save:
- key conclusions
- key logic
- current step
- goal
- next-step set
- blockers
- relevant files
- durable rules for promotion

## Memory quality gates

### 1. Admission gate
Only durable, reusable, or decision-relevant information belongs in `MEMORY.md`.

### 2. Deduplication gate
Prefer updating an existing rule over creating a repeated one.

### 3. Expiration gate
Temporary or phase-bound information should stay out of long-term memory unless labeled.

### 4. Compression gate
Prefer short structured entries over narrative summaries.

## Why this is faster

- smaller restore set
- higher signal-to-noise ratio
- fewer duplicate hits
- shorter memory reads
- less context waste
- high-priority data lives in faster retrieval lanes
- read depth is reserved for what matters most

## Why this loses less data

- quick save exists as a low-friction backup path
- handoff keeps the latest actionable state
- restore prioritizes the most important layers first
