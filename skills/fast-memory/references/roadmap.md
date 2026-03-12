<!-- Author: jim -->

# Fast Memory Roadmap

## Current stage

Rule-complete, automation-light.

The system already has:
- layered memory
- priority-aware storage
- retrieval-aware reading depth
- anti-pollution rules
- quick save and handoff logic

The system does not yet fully automate:
- classification
- save planning
- restore planning
- decay management
- working-set management

## Next step

Implement the recent full-session buffer mechanism.

Goal:
- retain the most recent 1 or 3 full sessions as a short-term raw buffer
- continue extracting structured near-term memory from them
- use full-session history as a fallback when structured memory is insufficient
- define when an old full session can be removed safely

Success condition:
The system can answer most recent-work questions from structured memory, and can still fall back to full-session history when needed.

Suggested output shape:

```md
## Memory Save Plan
- Class:
- Priority:
- Timeliness:
- Criticality:
- Lane:
- Completeness: rich | residual | skip
- Save to:
- Reason:
```

This is the fastest path from rules to usable execution.

## Step after next

Turn session restore into stable execution on top of the recent full-session buffer.

Goal:
At session start, consistently decide:
- which recent content to load first
- what the important content is inside that recent content
- what the current work is
- what the logic, current step, and goal are
- when to rely on structured memory
- when to fall back to full-session history
- what the final restored summary should contain

Suggested output shape:

```md
## Memory Restore Plan
- Primary source:
- Secondary source:
- Deep-read targets:
- Summary should include:
- Skip:
```

## Later steps

### 1. Decay manager
Automatically lower storage and retrieval priority for low-value, stale, rarely used information.

### 2. Recent working set manager
Maintain a hot set for the last 1 session and a warm set for the last few related sessions.

### 3. Promotion manager
Promote stable repeated logic into long-term memory when it becomes durable enough.

## Guiding principle

Do less, but do the right thing earlier.
