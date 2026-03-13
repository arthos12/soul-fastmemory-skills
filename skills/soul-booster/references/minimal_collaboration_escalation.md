# Minimal Collaboration Escalation

## Purpose
When user input is required, escalate only the smallest necessary collaboration package.

## Rule
Before asking the user anything, first finish:
- all independent reasoning
- all independent file updates
- all independent checks
- all independent safe execution

Then send only:
1. what is already done
2. what exact blocker remains
3. what single decision / input is needed
4. what will happen after the user replies

## Bad pattern
- dumping unfinished thinking to the user
- asking the user to do the next step when the bot could do it
- asking broad exploratory questions without narrowing the blocker

## Good pattern
- "Done A/B/C. Blocked only on X. If you reply Y, I will do Z next."

## Goal
Minimize user burden while preserving forward progress.
