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

Build a lightweight save planner.

Goal:
Given a piece of session content, decide:
- class
- priority
- timeliness
- criticality
- lane
- completeness level
- save target

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

Build a restore planner.

Goal:
At session start, decide:
- which layer to read first
- which snippets to read shallowly
- which snippets to read deeply
- what final restored summary should contain

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
