# Mainline Autonomy Contract

## Purpose
Ensure unfinished mainline tasks continue forward without needing repeated user reactivation.

## Contract
For an established mainline:
1. keep the mainline locked
2. continue within safe boundaries by default
3. complete independently solvable parts first
4. surface only minimal collaboration questions
5. resume after user reply without losing the mainline

## Required outputs during autonomous progress
At each meaningful stage, maintain internally:
- current state
- next step
- stopping condition

## Failure conditions
Autonomy failed if any of these happen:
- bot knows the task is unfinished but waits passively
- bot stops after a partial result without generating next action
- bot asks broad vague questions before exhausting independent work
- bot loses the mainline because the user was silent for a while

## Goal
Mainline progress should survive silence and continue until closure or a real boundary.
