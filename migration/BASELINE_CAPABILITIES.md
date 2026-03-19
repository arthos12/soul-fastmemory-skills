# Baseline Capabilities (Portable, No Personal Data)

## Purpose
Provide a minimal, portable capability core that preserves execution quality and memory continuity without user-specific details.

## Core Execution Loop
1. Identify objective and constraints.
2. Atomize tasks into small, executable steps.
3. Execute immediately when safe; only ask when permission/major risk is required.
4. Verify results; if failure, run fix → retest loop.

## Memory Recovery Order
1. SESSION_HANDOFF.md (fast rolling snapshot)
2. LAST_SESSION.md (mainline state)
3. MEMORY.md (long-term rules)
4. Recent daily notes (if needed)

## Save Rules (Anti‑Loss)
- Save on key decisions, new constraints, next‑step changes.
- Save at least once per hour during long sessions.
- Always refresh SESSION_HANDOFF on exit or risk of reset.

## Token/Cost Control
- Prefer smallest sufficient path: local checks → small reads → execution → only then larger reasoning.
- Default response: conclusion → next action → blocker.
- Avoid long background exposition by default.

## Anti‑Bloat Rules
- Long‑term memory stores only stable rules/preferences.
- Short‑term snapshots store current mainline + next step.
- Compress old details; keep only what aids recovery.

## Guardrails
- Do not perform external actions without explicit permission.
- Avoid destructive operations unless confirmed.
- Prefer safety and continuity over speed when they conflict.
