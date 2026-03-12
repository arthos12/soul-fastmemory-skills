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

Implement the storage lifecycle as a stable execution rule.

Goal:
- keep recent sessions fully preserved as hot data
- move sessions older than about 3 days into extracted structured storage
- detect when extracted storage becomes too large
- perform second-pass extraction on colder / lower-priority content
- keep the system compact without losing core logic

Success condition:
Storage stays layered and compact while preserving the important logic and recovery value.

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

Automate transfer, downgrade, and cleanup decisions.

Goal:
- decide when a recent session should leave the hot layer
- decide when extracted storage is too large
- decide which colder content should be downgraded into second-pass summaries
- decide when the old raw session can be safely removed after transfer

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
