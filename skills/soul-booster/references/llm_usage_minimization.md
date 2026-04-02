# LLM Usage Minimization

## Purpose
Reduce unnecessary model calls, call frequency, and token usage.
Use larger / slower / more expensive model reasoning only when the task actually needs it.

## Core rule
Do not spend model calls or tokens by default.
First decide whether the task can be solved by:
- direct answer from current context
- local file read / small retrieval
- simple deterministic action
- concise reasoning without expanded explanation

Only escalate to heavier model usage when these are insufficient.

## Default policy

### 1. Prefer the smallest sufficient path
Default order:
1. direct concise answer
2. small file read / targeted retrieval
3. deterministic edit / execution
4. normal reasoning
5. heavier reasoning / broader context only if necessary

### 2. Trigger conditions for heavier model usage
Escalate only when at least one is true:
- the task is high risk or high ambiguity
- a wrong answer would be costly
- multiple conflicting facts must be reconciled
- deeper reasoning clearly improves the outcome
- the user explicitly asks for deep analysis / long-form design / broad comparison

### 3. Anti-waste rules
- Do not reread large files when a targeted snippet is enough.
- Do not repeat already known context in long summaries.
- Do not generate long explanations before confirming they are needed.
- Do not use broad scans when targeted retrieval is enough.
- Do not invoke external model-like reasoning patterns for trivial tasks.

### 4. Compression rules
- answer conclusion first, details second
- read/search in small slices
- write compact summaries, not long narrative logs
- keep recovery files short and high-signal
- when using a larger context, extract the minimum durable result afterward

### 5. Reuse-before-regenerate rule
Before spending more tokens, check whether the answer/work already exists in:
- current context
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `TASKS.md` / `tasks/*`
- `MEMORY.md`
- recent daily note

## Goal
Spend tokens where they create real leverage, not where local structure or concise reasoning already solves the task.
