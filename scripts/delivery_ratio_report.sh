#!/usr/bin/env bash
set -euo pipefail

# Delivery ratio report (evidence-only)
# Usage: scripts/delivery_ratio_report.sh

BACKLOG="tasks/DELIVERY_BACKLOG.md"
if [[ ! -f "$BACKLOG" ]]; then
  echo "missing $BACKLOG" >&2
  exit 2
fi

pending=$(grep -cE '^-[[:space:]]\[[[:space:]]\][[:space:]]' "$BACKLOG" || true)
mvc=$(grep -cE '^-[[:space:]]\[m\][[:space:]]' "$BACKLOG" || true)
done=$(grep -cE '^-[[:space:]]\[x\][[:space:]]' "$BACKLOG" || true)
total=$((pending + mvc + done))

pct_done=0
pct_mvc=0
if [[ $total -gt 0 ]]; then
  pct_done=$(( 100 * done / total ))
  pct_mvc=$(( 100 * mvc / total ))
fi

echo "# Delivery ratio"
echo "- pending=$pending"
echo "- mvc=$mvc"
echo "- done=$done"
echo "- total=$total"
echo "- mvc_pct=${pct_mvc}%"
echo "- done_pct=${pct_done}%"

echo

echo "## pending list"
grep -E '^-[[:space:]]\[[[:space:]]\][[:space:]]' "$BACKLOG" || true
