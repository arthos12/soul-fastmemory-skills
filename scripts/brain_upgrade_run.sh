#!/usr/bin/env bash
set -euo pipefail

# Run one brain-upgrade micro-cycle (P0 then P1) and leave evidence artifacts.
# Does NOT message user; produces files only.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TS_UTC="$(date -u +%F\ %T)Z"

# P0: log one correction+verification stub (caller should edit if needed)
mkdir -p data/brain_evolution
{
  echo "## ${TS_UTC}"
  echo "- 问题：" 
  echo "- 硬纠偏：" 
  echo "- 最小验证：" 
} >> data/brain_evolution/evolution_log.md

# P1: run a filtered batch
mkdir -p data/polymarket
python3 scripts/polymarket_pull.py --limit 80 --out data/polymarket/markets_latest_source.jsonl >/dev/null
python3 scripts/polymarket_filter.py --in data/polymarket/markets_latest_source.jsonl --out data/polymarket/markets_latest_filtered.jsonl --limit 30 >/dev/null
python3 scripts/polymarket_predict.py --in data/polymarket/markets_latest_filtered.jsonl --out data/polymarket/predictions_latest_v1.jsonl --limit 20 >/dev/null
python3 scripts/polymarket_score.py data/polymarket/predictions_latest_v1.jsonl > data/polymarket/score_latest_v1.json

echo "OK"