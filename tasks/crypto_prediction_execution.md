# Crypto Prediction Execution

## Goal
Start real crypto prediction case generation immediately, then selectively convert only qualified predictions into trade candidates.

## Why it had not started
1. I stayed too long in planning/rule-fixing mode.
2. I treated prediction-work architecture as prerequisite and delayed real batch execution.
3. I failed to convert the explicit requirement into an immediate executable atom.

## Immediate fix
- Start with a minimal live batch using public market data
- Generate many prediction cases first
- Gate trade candidates with simple filters
- Score later and iterate

## Current atoms
- [x] create first crypto batch script
- [x] run first live batch
- [ ] inspect top candidates
- [ ] decide next expansion: more pairs / more horizons / scoring loop
