# Prediction Case Monitoring

## Goal
Monitor open prediction cases and make sure results are checked when they become due.

## Core process
1. create case
2. set checkAt
3. mark open
4. when due, fetch/check real result from a real data source
5. only after real-result check, mark checked / stale / invalid
6. write actualResult
7. external comments / user feedback / market chatter may be stored only as reference, not as actualResult
8. feed into scoring / profitability analysis

## Current risk
The biggest risk is not wrong prediction alone, but failing to check results after prediction.

## Current action atoms
- [ ] build due-case scanner
- [ ] build result-check updater
- [ ] connect short-horizon crypto predictions first
- [ ] connect longer event predictions second
