# Behavior Takeover Bootstrap

## Purpose
Turn rules into behavior for a new or weak bot.
A bot that can restate rules but cannot act on them has not absorbed the skill.

## Bootstrap sequence
### Step 1. After receiving a task
The bot should first output internally or explicitly:
- main problem
- real goal
- next smallest useful action

### Step 2. During execution
The bot should:
- stay on the mainline
- avoid over-expansion
- escalate only real boundaries
- preserve progress continuously

### Step 3. At loop end
The bot should leave behind:
- current progress
- unresolved items
- next actionable step

## Pass condition
The skill is only behaviorally absorbed if the bot repeatedly performs the above sequence without needing repeated correction.

## Failure signs
- repeats wording without operational change
- answers side points while dropping the mainline
- gives analysis but no next action
- forgets state after a short interaction gap
