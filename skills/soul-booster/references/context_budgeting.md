# Context Budgeting

## Purpose
Control context growth so the agent uses only the minimum context needed for accurate work.

## Core rule
Treat context as a scarce budget, not a free dump area.

## Budgeting rules

### 1. Keep only active working state in the hot path
Preferred hot context:
- current mainline
- current step
- next step
- key constraints
- key files

### 2. Move durable information into files
Use:
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `TASKS.md`
- `tasks/*`
- `MEMORY.md`
- daily note for same-day detail

### 3. Read narrowly
- locate first
- read the minimum needed snippet
- avoid full-file rereads unless clearly justified

### 4. Reuse extracted conclusions
If a conclusion already exists in durable form, reuse it before re-expanding the old context.

### 5. Avoid context pollution
Do not preserve low-value chatter, repeated summaries, or long narrative logs in the hot path.

## Goal
Keep model context short, high-signal, and directly useful for current execution.
