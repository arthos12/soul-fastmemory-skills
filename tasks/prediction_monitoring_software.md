# Prediction Monitoring Software

## Goal
Build local software/scripts that support my analysis for:
- Polymarket event prediction + paper trading + settlement + win-rate tracking
- BTC / lobster continuous monitoring + directional prediction tracking + win-rate tracking

## Polymarket core objectives (explicitly locked by Jim)
1. Find which market/category/type my predictions are most accurate on, and what the win rate is.
2. Measure post-quant-trading results: order win rate and return / profitability after applying sizing rules.

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
### Line A (primary): fast-feedback prediction loop
1. Build 4h / 24h prediction journal and scorer first
2. Record large-volume prediction samples with timestamp, horizon, direction, range, confidence, invalidation
3. Score after window close automatically
4. Compare short-horizon, medium-horizon, and grid-style behavior side by side
5. Output directional accuracy / range hit rate / calibration / simple pnl-style metrics

### Line B (parallel supplement): Polymarket
1. Add short-cycle market selection layer first
2. Continue paper orders for event-market training and later settlement
3. Add resolver/settlement script
4. Add portfolio risk cap and order throttling
5. Add equity curve / summary metrics
6. Add accuracy-by-market-type report
7. Add continuous monitor runner

### Horizons / styles to test
- ultra-short: 4h
- short-mid: 24h
- mid: 3d / 7d when useful
- grid-style: repeated band/range prediction around current price

## Acceptance
- can run without manual babysitting
- can record predictions and later score them
- can report directional accuracy and trading-style outcome
- can continue improving during idle time

## Next step
Implement Polymarket settlement + bankroll cap first, then start BTC/lobster prediction journal.
