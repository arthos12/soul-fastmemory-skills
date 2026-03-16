# Short Horizon Result Check

## Goal
Ensure short-term predictions are not only generated, but actually checked when results arrive.

## Rule
- short-term predictions (4h / 24h / 3d) must default to result-check capable
- long-term predictions can stay pending, but must remain checkable when their outcome time arrives
- prediction without later result check counts as incomplete

## Current action atoms
- [x] start short-term crypto prediction batch
- [ ] add result-check script for 4h / 24h crypto predictions
- [ ] add pending-check list for longer event predictions
- [ ] ensure old predictions can be reloaded and checked when result time arrives
