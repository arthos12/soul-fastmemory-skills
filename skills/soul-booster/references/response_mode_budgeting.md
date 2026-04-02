# Response Mode Budgeting

## Purpose
Make token-saving behavior executable by defining reply modes and context budgets.

## Core rule
Default to the lightest mode that can still solve the task correctly.
Upgrade only when complexity, ambiguity, or risk clearly requires it.

## Modes

### Light mode
Use for:
- yes/no questions
- current status
- small confirmations
- short direct instructions
- simple execution acknowledgements

Reply shape:
- 1 to 4 short lines
- default structure: conclusion / next step / blocker(if any)

Context budget:
- current user message
- one or two relevant short file snippets if needed
- do not expand broad history by default

### Mid mode
Use for:
- small comparisons
- compact diagnosis
- short plan with a few steps
- limited requirement reconciliation

Reply shape:
- 5 to 12 lines
- conclusion first, then compact structure

Context budget:
- current message
- minimal active task state
- a few targeted snippets
- avoid whole-file rereads

### Heavy mode
Use only for:
- deep debugging
- high-risk decisions
- complex architecture/design
- major ambiguity with costly error risk

Reply shape:
- only as long as needed
- still lead with conclusion
- structure before detail

Context budget:
- only the justified extra context
- if history is needed, prefer distilled file state over long chat replay

## Upgrade triggers
Upgrade mode only if at least one is true:
- wrong answer cost is high
- ambiguity remains after local inspection
- multiple conflicting facts must be reconciled
- the task truly needs deep design or deep diagnosis
- the user explicitly asks for depth

## Anti-waste rule
Do not use heavy mode just because the topic sounds important.
Use heavy mode only when the work itself requires it.

## Goal
Turn “be concise” into a stable operating rule with explicit mode boundaries.
