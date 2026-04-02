# Idle Local-First Maintenance

## Purpose
Define what the agent should do during idle windows while minimizing unnecessary model usage.
Prefer local compute, local files, and deterministic checks first.

## Core rule
During idle windows, prefer local-first maintenance.
If a task can be done with local file inspection, deterministic scripts, small diffs, or concise reasoning, do that first.
Be cautious with any action pattern that would trigger large-context or repeated heavy model usage.

## Default idle task set
When safe and relevant, prioritize:
1. continue the unfinished mainline task
2. check whether fast-recovery layers are current
3. check whether important requirements were written but not executed
4. check whether new symptoms / "炎症" indicate a shared root cause
5. tighten task files, handoff files, and acceptance items
6. improve local rules / references that reduce repeated failures

## Local-first checks
Use local-first methods for:
- reading `TASKS.md`, `tasks/*`, `LAST_SESSION.md`, `SESSION_HANDOFF.md`
- checking timestamps / diff / file presence
- spotting unresolved checklist items
- classifying failure types
- tracing repeated issues to common causes
- updating compact local docs and references

## Escalation rule
Only consider heavier model usage if at least one is true:
- local evidence is insufficient
- the reasoning ambiguity remains high after local inspection
- a broad comparison or deep design is truly required
- the expected benefit clearly justifies the token cost

## Anti-waste rule
Idle maintenance itself must not become token-heavy busywork.
Prefer small, durable, leverage-producing improvements over repeated broad scans or verbose summaries.

## Goal
Make idle windows produce real local progress while preserving token budget.
