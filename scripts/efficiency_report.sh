#!/usr/bin/env bash
set -euo pipefail

# Summarize efficiency metrics (evidence)
# Usage: scripts/efficiency_report.sh [n]

N="${1:-20}"
FILE="data/efficiency/metrics.jsonl"

if [[ ! -f "$FILE" ]]; then
  echo "missing $FILE" >&2
  exit 2
fi

echo "# Efficiency metrics (last $N)"
tail -n "$N" "$FILE" | cat
