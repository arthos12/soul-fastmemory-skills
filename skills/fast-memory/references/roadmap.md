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

Turn new-session restore into a fixed execution flow.

Goal:
- load recent content first
- identify important content inside recent content
- find the most important and recently important content
- reconstruct the work through logic, current step, and goal
- use structured memory first
- fall back to the recent full-session buffer when needed
- produce a stable restored state

Success condition:
New-session recovery follows the same flow repeatedly and restores the main work with less drift.

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

Refine retention and deletion automation for old full-session buffers.

Goal:
- keep recent full-session buffers available as short-term fallback
- detect when core logic has already been extracted
- detect when a full session has gone unused long enough
- remove old full-session buffers safely without harming recovery quality

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
