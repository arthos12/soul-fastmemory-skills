#!/usr/bin/env bash
set -euo pipefail

# Idle runner: advances work only if there is pending work.
# "Pending" is defined by a simple switch file to avoid wasting cycles.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SWITCH="data/brain_evolution/IDLE_ENABLE"
LOG="data/brain_evolution/idle_cycle_reports.log"
mkdir -p data/brain_evolution

# Default: enabled if switch file missing
if [[ -f "$SWITCH" ]]; then
  val=$(tr -d ' \t\r\n' < "$SWITCH" | tr '[:upper:]' '[:lower:]')
  if [[ "$val" == "0" || "$val" == "false" || "$val" == "off" ]]; then
    exit 0
  fi
fi

# Run one micro-cycle and append evidence report
bash scripts/brain_upgrade_run.sh >/dev/null 2>&1 || true
{
  echo "===== $(date -u +%FT%TZ) ====="
  bash scripts/progress_report.sh 15 || true
  echo
} >> "$LOG"
