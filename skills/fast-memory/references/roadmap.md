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

Apply the execution parameters consistently in real usage.

Goal:
- use the 3-session hot buffer by default
- move sessions older than 3 days into extracted storage
- detect oversized extracted storage
- downgrade colder content consistently
- keep the system compact without losing the main logic

Success condition:
The same storage decisions repeat consistently across similar cases.

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

Automate transfer, downgrade, and cleanup decisions more precisely.

Goal:
- detect hot-to-structured transfer timing reliably
- detect cold-content downgrade candidates reliably
- remove old raw sessions safely after transfer
- keep recovery quality stable while storage stays compact

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
