# Prediction Root Capability Guard

## Purpose
Protect prediction work from being pulled off-course by chat heat, fragmented asks, or surface-level demand pressure.

## Core rule
For prediction-related work, root capability is always more important than surface conversational drift.

## Root capability set
1. prediction base model quality
2. calibration quality
3. evidence update / repricing quality
4. market selection quality
5. no-trade / trade gate quality
6. sizing / risk quality
7. scoring and review loop quality
8. information-boundary awareness
9. profitable-scenario detection

## Drift test
Before major prediction work, ask:
- Does this action improve a root capability?
- Does it improve future win rate / edge quality / profit probability?
- Is it just satisfying surface chat pressure?
- If I skip this action, does prediction core actually get worse?

If the action mainly satisfies surface chat pressure and does not improve root capability, downgrade it.

## Default correction
1. return to main goal: profitable prediction ability
2. identify root capability gap
3. take the smallest action that improves the root capability
4. only then handle surface reporting needs
