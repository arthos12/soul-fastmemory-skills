# Idle Progress Audit

## Purpose
Audit whether the agent really advances meaningful work during idle windows, instead of merely claiming it can.

## Audit dimensions

### 1. Mainline continuity
Check:
- Is there a clearly locked mainline task?
- After replying, is there an explicit next step?
- If the user goes silent, can the agent continue within safe boundaries?

Failure signs:
- reply ends the work loop
- no next step exists
- task progress depends on another user ping

### 2. Recovery-layer support
Check:
- Is the current mainline written into `LAST_SESSION.md` or `SESSION_HANDOFF.md`?
- Is there a `Saved At` timestamp?
- Can `/new` + `加载数据` restore the autonomous work state?

Failure signs:
- only daily log updated
- no fast-recovery layer updated
- restored state lacks next action

### 3. Boundary discipline
Check:
- Does the agent continue independently only inside safe boundaries?
- Does it compress real blockers into minimal collaboration questions?

Failure signs:
- waits too early
- crosses risky boundary blindly
- asks vague broad questions before finishing independent work

### 4. Useful idle action quality
Check:
- Are idle actions high-value and tied to the active mainline?
- Do they improve task completion, recovery, logic, or understanding?

Failure signs:
- unrelated busywork
- generic cleanup that does not help the mainline
- repeated note-taking without forward movement

## Minimum pass standard
The idle-progress ability passes only if all are true:
1. mainline is explicit
2. next step is explicit
3. fast-recovery layer is updated
4. idle action improves real task progress or recoverability
5. safe-boundary discipline is preserved

## Recommended correction path
If the audit fails, fix in this order:
1. restore mainline + next step
2. update fast-recovery layer
3. tighten blocker detection
4. reduce non-mainline idle work
5. rerun `/new` + `加载数据` acceptance
