# High Frequency Conversation Saving Plan

## Goal
When Jim and I talk frequently, reduce model-call waste while keeping urgent replies fast and important work continuously moving.

## Core method
### 1. Merge many small asks into one execution batch
- If several nearby messages share one main goal, merge them into one task batch.
- Reply once with the compressed result instead of answering each sub-message separately.
- Treat high-frequency chat as a rate-limit risk: fewer rounds with higher completion density beat many tiny replies.

### Rate-limit view
Handle conversation cost on 3 axes:
- request frequency: too many small turns burns request budget
- token flow: too much text per turn burns token budget
- daily total: too many low-yield turns reduce the number of useful sessions available that day

### 2. Priority split
Always split incoming items into only two buckets:
- immediate-next-turn: urgent replies, critical blockers, real-time checks Jim explicitly needs now
- batch-next-cycle: non-urgent edits, cleanup, structure work, follow-up implementation

### 3. Default reply shape
- result
- action done / next action
- blocker only if real

### 4. Reduce repeated context cost
- move reusable instructions into files
- move multi-step plans into task files
- move repeated background into memory / handoff files
- do not restate old background unless needed for current action

### 5. Batch execution preference
Prefer:
- one bigger batch write over many tiny chat turns
- one script run over many manual checks
- one summary after execution over many intermediate narrations

## Immediate-next-turn rule
Anything urgent enough to deserve an immediate reply should be added to the next executable turn as a high-priority atom, not left floating in chat.

## Acceptance
- fewer back-and-forth clarification turns
- fewer long explanations
- more completed actions per reply
- urgent asks answered quickly without dragging the whole session into high token burn
