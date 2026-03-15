# Brain Prediction Upgrade

## Goal
Upgrade the brain layer for prediction/analysis so it becomes more accurate, more auditable, and better connected to execution.

## Locked priorities (confirmed by Jim)
1. Dynamic belief revision / dynamic repricing
2. Classification + model-routing judgment
3. Post-prediction review and attribution
4. Probability / range / window / invalidation standardized output
5. Better abstain / no-trade / low-confidence behavior
6. Immediate execution after committing to a real-time check; do not stall with confirmation-only replies

## Why
Current weakness is not only lack of models, but lack of:
- dynamic probability updates when evidence changes
- fast recognition of which model family to use
- structured postmortem on prediction errors
- strict standardized prediction outputs
- refusal/no-trade gates for noisy markets

## Execution lines
### A. Prediction output protocol
- standard fields: target, timeWindow, direction, probability, range, invalidation, confidence
- enforce use in BTC/lobster/event predictions

### B. Dynamic repricing
- define evidence update fields
- add probability revision log format
- compare first prediction vs revised prediction vs final outcome

### C. Classification router
- label prediction type: event / threshold / short-term price / noisy meme / macro / political / etc.
- link each type to default model family and caution rules

### D. Review attribution
- after result, classify miss cause: understanding / evidence / logic / timing / sizing / noise
- accumulate attribution stats

### E. Abstain / no-trade gate
- define when to avoid prediction or avoid trade
- low-confidence and high-noise cases should be explicitly downgraded

### F. Real-time check execution gate
- if I say I will check current/real-time status, immediately execute the check with tools
- do not send extra confirmation-only messages before the actual fetch/check happens
- if identifier/ticker/link may already exist in context, search local context/files first before asking Jim again
- only ask Jim when the missing identifier truly cannot be recovered locally

## Acceptance
- predictions become standardized and scoreable
- revised probabilities are logged instead of silently overwritten
- categories can be compared by hit rate
- misses produce attribution, not just win/loss
- noisy cases can be skipped intentionally

## Next step
Implement prediction output protocol first, then classification router and review attribution.
