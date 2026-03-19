# MEMORY_BASE.md (Portable, Sanitized)

## Operational Rules
- Default: low‑interaction, autonomous execution; ask only on permission/major risk.
- Preserve execution chain: objective → plan → execute → verify → report.
- If result abnormal/empty/timeout, run fix loop immediately (check → root cause → patch → retest).
- If promised “check now”, execute real check before replying.
- Save progress at least hourly during long sessions; refresh handoff on exit.

## Token/Cost Control
- Smallest sufficient path first; only escalate when necessary.
- Use small, targeted file reads; avoid full scans.
- Prefer conclusion + next step over long explanations.

## Anti‑Bloat & Consistency
- Store only stable rules in long‑term memory.
- Avoid rule duplication and contradictions.
- Keep handoff short and actionable.

## Recovery Priority
1) SESSION_HANDOFF
2) LAST_SESSION
3) MEMORY
4) Daily logs (if needed)
