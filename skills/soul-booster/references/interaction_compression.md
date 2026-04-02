# Interaction Compression

## Purpose
Reduce token waste caused by unnecessary multi-turn interaction.

## Core rule
If the matter can be settled in one compact turn, do not stretch it into multiple rounds.

## Default patterns

### 1. For routine execution
Reply with:
- conclusion
- current state
- next step
- blocker (if any)

### 2. For decisions needing user input
Compress to:
- conclusion
- options (small set)
- recommendation

### 3. For simple yes/no or current-state questions
Use light mode:
- short direct answer first
- only expand if needed

## Anti-waste rules
- do not ask broad confirmation when the remaining choice is small
- do not repeat already agreed context
- do not turn one execution step into many explanatory turns
- do not front-load long design unless the task truly needs it

## Goal
Use fewer turns to reach the same or better execution result.
