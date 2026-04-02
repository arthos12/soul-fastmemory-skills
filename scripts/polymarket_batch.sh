#!/usr/bin/env bash
set -euo pipefail

# Unified capability: generate one Polymarket training batch.
# Usage:
#   scripts/polymarket_batch.sh --limit 80 --pick 30 --pred 20 --tag batch6

LIMIT=80
PICK=30
PRED=20
TAG="batch"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2;;
    --pick) PICK="$2"; shift 2;;
    --pred) PRED="$2"; shift 2;;
    --tag) TAG="$2"; shift 2;;
    *) echo "unknown arg $1" >&2; exit 2;;
  esac
done

TS="$(date -u +%F)"
SRC="data/polymarket/markets_${TAG}_source.jsonl"
FILT="data/polymarket/markets_${TAG}_filtered.jsonl"
PRED_OUT="data/polymarket/predictions_${TS}_${TAG}_v1.jsonl"
SCORE="data/polymarket/score_${TS}_${TAG}_v1.json"

mkdir -p data/polymarket
python3 scripts/polymarket_pull.py --limit "$LIMIT" --out "$SRC" >/dev/null
python3 scripts/polymarket_filter.py --in "$SRC" --out "$FILT" --limit "$PICK" >/dev/null
python3 scripts/polymarket_predict.py --in "$FILT" --out "$PRED_OUT" --limit "$PRED" >/dev/null
python3 scripts/polymarket_score.py "$PRED_OUT" > "$SCORE"

echo "OK"
echo "- $SRC"
echo "- $FILT"
echo "- $PRED_OUT"
echo "- $SCORE"
