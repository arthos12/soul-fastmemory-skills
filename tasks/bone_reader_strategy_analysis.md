# BoneReader strategy analysis

## Goal
Reverse-engineer BoneReader enough to borrow useful structure without blindly copy-trading.

## Current confirmed facts
- Profile page exposes structured data via __NEXT_DATA__.
- proxyWallet found.
- pnl is strong (~832k visible in current page data).
- traded count ~39k.
- market focus is PM crypto short-cycle up/down.

## Working hypothesis
BoneReader is not pure copy-tradable alpha. Likely a mixed strategy:
1. near-resolution closing trades
2. short-cycle direction trades
3. mispricing / low-price-to-fair reversion trades

## Required next steps
- [ ] extract visible profile data into file
- [ ] summarize 1D/1W/1M/ALL pnl curves
- [ ] classify visible trade styles
- [ ] create our own simulated order rules inspired by structure, not copy entries
- [ ] compare our paper orders vs BoneReader-style structure
