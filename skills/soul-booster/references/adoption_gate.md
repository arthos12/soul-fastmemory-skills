# Adoption Gate

## Purpose
Prevent false claims of successful skill adoption.

## Rule
Reading, quoting, summarizing, or referencing the skill does NOT count as adoption.
Adoption counts only when the bot's behavior changes in the same or next real task.

## Minimum pass conditions
A bot only passes basic adoption if it can do all of the following in a real turn:
1. identify the user's real goal
2. answer the main question first
3. split compound questions when present
4. avoid keyword hijack
5. give one sensible next action when the goal is clear

## Fail conditions
Treat adoption as failed if the bot mainly does any of these:
- quotes the skill instead of using it
- explains future improvement instead of showing changed behavior
- answers a related question instead of the real question
- gives nice structure but misses the point

## Goal
Adoption must be behavior-visible, not wording-visible.
