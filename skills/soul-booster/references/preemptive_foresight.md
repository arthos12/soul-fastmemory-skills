# Preemptive Foresight

## Purpose
Turn preemptive prediction into a bottom-layer capability instead of a task-specific trick.
The agent should not wait for problems to appear before improving the plan.

## Core definition
Preemptive foresight means:
Before answering, executing, migrating, or committing to a plan, run the minimum necessary forward-looking check.

It asks:
- Is this path actually feasible?
- Where is it most likely to fail first?
- Which dependencies are missing now but will block later?
- Which boundary will require user confirmation?
- What backup path should exist if the main path breaks?
- If this is transferred to another bot or environment, which parts will survive and which will fail?

## Why it is a bottom-layer capability
It improves not only one task, but the quality of:
- planning
- execution success rate
- autonomous progress
- migration to other bots
- reduction of future rework

## 4 sub-capabilities
### 1. Path foresight
Judge whether the current route is really viable.

### 2. Failure foresight
Predict the most likely failure points before they happen.

### 3. Boundary foresight
Predict where permissions, risk, or uncertainty will require user confirmation.

### 4. Transfer foresight
Predict what will happen when the same logic is moved to another bot, environment, or later session.

## Planning rule
When making a plan, do not only design the current workable path.
Also evaluate:
- likely future blockers
- dependency gaps
- high-probability failure nodes
- fallback paths
- confirmation boundaries

## Upgrade loop
Preemptive foresight should improve continuously:
1. predict before acting
2. execute
3. compare real result vs prediction
4. record misses / correct hits
5. update future foresight patterns

## Anti-overuse rule
Do not turn foresight into endless speculation.
Run the minimum necessary forward-looking layer, then return to action.

## Goal
Make plans more forward-looking, reduce rework, and help the agent act more like a mature decision-maker.
