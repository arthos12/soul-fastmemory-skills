# Minimal Closure Acceptance

## Purpose
Judge a weak bot by real behavior, not by whether it can repeat rules.

## Test rule
A weak bot passes a minimal loop only if it can do all of the following in a real task:
1. identify the main problem correctly
2. identify the real goal correctly
3. avoid obvious drift or side-tracking
4. perform the next useful action
5. preserve progress / unresolved items / next step

## Failure rule
If the bot can explain the rules but fails one of the five checks above, the skill is not yet behaviorally installed.

## Goal
Use real-task closure as the acceptance standard.
