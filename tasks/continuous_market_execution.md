# Continuous Market Execution

## Goal
Fix the failure of non-continuous monitoring, non-continuous prediction, and non-continuous trade candidate generation in real markets.

## Confirmed failure
In the last cycle, lobster and BTC were not continuously monitored, predicted, and converted into ongoing trade actions/candidates.
This is treated as an execution failure, not a minor omission.

## Required continuous loop
For selected live markets (starting with BTC and lobster):
1. monitor continuously
2. generate rolling predictions continuously
3. generate rolling trade candidates continuously
4. check results when due
5. update model/rules from results

## Current first markets
- BTC
- lobster

## Current action atoms
- [ ] create rolling prediction runner for BTC/lobster
- [ ] create rolling candidate ledger
- [ ] create due-result checker
- [ ] ensure no cycle ends without fresh monitored state and fresh prediction state

## Hard rule
If a live market is chosen as an active training market, it must not fall into long gaps of no monitoring and no prediction. That counts as a mainline break.
