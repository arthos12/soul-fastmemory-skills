# Fragmented Requirement Handling

## Purpose
Handle fragmented user requirements without losing important ones and without cluttering the system with low-value noise.

## Core rule
When the user gives fragmented requirements across multiple short messages:
1. record them
2. classify them
3. decide whether they matter to the goal
4. if they matter, execute or route them into real execution tracking
5. if they do not matter, allow parking or loss

## Classification

### A. Goal-relevant requirement
Definition:
- changes the active goal
- changes execution method
- changes priority, boundary, acceptance, memory, recovery, or risk handling
- affects whether the mainline task will succeed or fail

Action:
- write it into the appropriate durable layer
- check whether execution is needed now
- if yes, do real execution
- if no, keep it in the correct waiting/parking structure

### B. Supporting but non-urgent item
Definition:
- useful, but not currently critical to the mainline
- can help future execution or maintenance

Action:
- store compactly in task/parking/reference layer
- do not let it interrupt the mainline unnecessarily

### C. Idle or low-value chatter
Definition:
- does not change goal, execution, memory, recovery, acceptance, or risk
- no durable reuse value

Action:
- do not force durable recording
- it may be safely dropped

## Execution rule
Do not treat “recorded” as “done”.
For every goal-relevant fragmented requirement, ask:
- does this need real execution now?
- does this change task state, recovery state, or rule state?
- has the execution actually happened, or was it only written down?

If real execution is needed, execute it or put it into explicit next-step tracking.

## Anti-loss rule
Important fragmented requirements must not be lost just because they were said briefly or across multiple messages.
The shorter the user message, the stronger the need for internal classification.

## Anti-clutter rule
Do not turn every fragmented message into durable memory.
Only keep what affects goal, method, boundary, acceptance, recovery, or repeated future value.

## Goal
Prevent important fragmented requirements from being forgotten while still keeping memory and token usage clean.
