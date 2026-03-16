# Conversation Batch Queue

## Purpose
Hold non-urgent but real items that should be merged into the next efficient execution batch instead of consuming many chat turns.

## Buckets
### immediate-next-turn
- urgent replies Jim needs now
- critical blockers
- real-time checks promised to Jim

### batch-next-cycle
- follow-up edits
- cleanup
- structure improvements
- non-urgent implementation work

## Current policy
- urgent items go to immediate-next-turn and are handled in the very next executable turn
- non-urgent items go to batch-next-cycle and should be merged before replying again
- do not let many small asks stay only in chat
