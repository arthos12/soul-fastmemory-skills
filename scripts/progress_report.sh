#!/usr/bin/env bash
set -euo pipefail

# Evidence-only progress report.
# Usage: scripts/progress_report.sh [minutes]

MINUTES="${1:-60}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "# Progress (last ${MINUTES} min)"

echo "## Files changed"
# list files (excluding .git) modified within MINUTES, with line counts when possible
mapfile -t files < <(find . -path './.git' -prune -o -type f -mmin "-${MINUTES}" -print | sed 's|^\./||' | sort)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "(none)"
  exit 0
fi

for f in "${files[@]}"; do
  if [[ -f "$f" ]]; then
    # count lines for text-ish files
    if file "$f" | grep -qiE 'text|json|xml|yaml|markdown|csv'; then
      lc=$(wc -l < "$f" | tr -d ' ')
      ts=$(stat -c '%y' "$f")
      echo "- $f | lines=$lc | mtime=$ts"
    else
      ts=$(stat -c '%y' "$f")
      sz=$(stat -c '%s' "$f")
      echo "- $f | bytes=$sz | mtime=$ts"
    fi
  fi
done


echo

echo "## Re-run commands (most recent pipeline)"
cat <<'CMD'
python3 scripts/polymarket_pull.py --limit 80 --out data/polymarket/markets_batch5_source.jsonl
python3 scripts/polymarket_filter.py --in data/polymarket/markets_batch5_source.jsonl --out data/polymarket/markets_batch5_filtered.jsonl --limit 30
python3 scripts/polymarket_predict.py --in data/polymarket/markets_batch5_filtered.jsonl --out data/polymarket/predictions_2026-03-15_batch5_v1.jsonl --limit 20
python3 scripts/polymarket_score.py data/polymarket/predictions_2026-03-15_batch5_v1.jsonl > data/polymarket/score_2026-03-15_batch5_v1.json
CMD
