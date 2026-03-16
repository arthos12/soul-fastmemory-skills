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

## New hard additions (2026-03-16)
### G. Self-test before waiting for user input
- when checking whether a capability is complete, first simulate likely Jim commands locally
- verify whether outputs, path choice, and result-improvement behavior are correct before asking Jim for more guidance
- then monitor real-world results over multiple runs

### H. Alternative-advance mode
- if missing data / blocked path / weak validation, do not stop by default
- expand substitute data, substitute reasoning, substitute validation, and substitute advancement level
- use substitute paths to keep progress moving until real-case validation is available

### I. Efficiency anomaly attribution
- when progress is slow, do not default to waiting for Jim
- detect slowdown, attribute root cause, remove low-yield actions, switch to higher-yield path, and re-measure efficiency

## Execution chain requirement (2026-03-16)
For prediction upgrades, default chain is fixed as:
problem -> solution -> requirement -> execution -> validation

Hard rules:
- Do not re-define what a problem is once the issue is already clear.
- After identifying a prediction bug or efficiency bug, compress it into an execution-ready requirement and task atom immediately.
- If the same prediction issue is explained for more than 1 round without new result improvement, treat it as stuck-in-middle-state and force execution.
- Execution layer must not rewrite goal/problem/acceptance on the fly; if the plan itself seems wrong, return to analysis layer explicitly.
- Success means changed behavior + changed file/rule/script + validation + better result movement; explanation alone does not count.
- When a problem is found, compress immediately into: lock main problem -> lock acceptance -> lock single path -> produce minimum action -> execute now.
- Second-pass plan audit must check only three things: does it solve the real problem, can it actually run through, and is it likely to pass validation/acceptance. If not, regenerate a different plan instead of expanding explanation.
- If multiple plan-audit passes still fail, stop self-looping and produce a final review package for Jim with only the minimum decision payload; after Jim picks, execute immediately.

## New core requirement (2026-03-16)
Prediction upgrade is now bound to a higher-level core ability requirement:
- reduce conversation count while increasing completed work
- reduce token waste while increasing delivered result density
- atomize problems and requirements before execution
- do not leave large numbers of requirements living only inside chat

Hard execution binding:
1. Any prediction-related request must first be compressed into requirement atoms and task atoms.
2. Explanation-only rounds are invalid; every round must include either direct execution, changed artifact, validation result, or a concrete blocker.
3. If a prediction-improvement discussion leaves multiple requirements unexecuted in chat, treat that as an execution failure, not as normal discussion.
4. Prediction work should prefer batch processing, scriptization, and reusable files so that future iterations cost fewer model calls.
5. Fast-feedback prediction loops are preferred over long-wait loops whenever they can produce more real samples faster.

## Next step
Implement prediction output protocol first, then classification router and review attribution. In parallel, apply self-test-before-waiting, alternative-advance mode, efficiency anomaly attribution, the problem->solution->requirement->execution->validation chain, and the new atomization + low-conversation high-output requirement to all prediction upgrade iterations.
