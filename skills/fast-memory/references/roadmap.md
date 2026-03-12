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

Implement the fixed content classification and storage-decision template in real usage.

Goal:
For actual session content, consistently decide:
- what kind of content it is
- which of the 6 importance levels it belongs to
- where it should be stored
- how completely it should be stored
- why

Success condition:
The same type of content should lead to similar storage decisions across sessions.

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

Turn the fixed session-restore template into stable execution.

Goal:
At session start, consistently decide:
- which recent content to load first
- what the important content is inside that recent content
- what the current work is
- what the logic, current step, and goal are
- which snippets need shallow reading
- which snippets need deep reading
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
