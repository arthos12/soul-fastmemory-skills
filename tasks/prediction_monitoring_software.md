# Prediction Monitoring Software

## Goal
Build local software/scripts that support my analysis for:
- Polymarket event prediction + paper trading + settlement + win-rate tracking
- BTC / lobster continuous monitoring + directional prediction tracking + win-rate tracking

## Confirmed user intent
Jim explicitly approved:
- do it without repeated asking
- continue during idle time
- include continuous monitoring
- include prediction win-rate measurement
- use software/scripts to support analysis

## Current status
### Done
- `scripts/polymarket_backtest_sim.py` — simulation backtest for binary outcomes
- `scripts/polymarket_paper_trade.py` — create paper orders from live predictions
- `scripts/polymarket_monitor_run.sh` — pull live markets -> predict -> generate paper orders
- live artifacts under `data/polymarket/`

### Not done
- auto settlement for resolved markets
- portfolio-level exposure cap / total bankroll constraint
- equity curve
- bucketed accuracy / ROI stats
- BTC/lobster monitoring scripts
- prediction journal + scoring for BTC/lobster

## Execution plan
### Line A: Polymarket
1. Add resolver/settlement script
2. Add portfolio risk cap and order throttling
3. Add equity curve / summary metrics
4. Add accuracy-by-market-type report
5. Add continuous monitor runner

### Line B: BTC / lobster
1. Define data source path(s)
2. Create local watcher scripts for price snapshots/time series
3. Record each prediction with timestamp + range + direction
4. Compare with realized move after window closes
5. Output win rate / range hit rate / directional accuracy

## Acceptance
- can run without manual babysitting
- can record predictions and later score them
- can report directional accuracy and trading-style outcome
- can continue improving during idle time

## Next step
Implement Polymarket settlement + bankroll cap first, then start BTC/lobster prediction journal.
