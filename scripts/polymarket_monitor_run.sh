#!/usr/bin/env bash
set -euo pipefail
cd /root/.openclaw/workspace
mkdir -p data/polymarket
TODAY_UTC="$(date -u +%F)"
SRC="data/polymarket/markets_monitor_${TODAY_UTC}.jsonl"
PRED="data/polymarket/predictions_monitor_${TODAY_UTC}.jsonl"
LEDGER="data/polymarket/paper_orders_${TODAY_UTC}.jsonl"
python3 scripts/polymarket_pull.py --limit 80 --active 1 --closed 0 --out "$SRC"
python3 scripts/polymarket_predict.py --in "$SRC" --out "$PRED" --limit 40
python3 scripts/polymarket_paper_trade.py --in "$PRED" --out "$LEDGER" --threshold 0.05 --sizing kelly --bankroll 100000 --kelly-scale 0.25
printf 'SRC=%s\nPRED=%s\nLEDGER=%s\n' "$SRC" "$PRED" "$LEDGER"
