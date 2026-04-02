#!/usr/bin/env bash
set -euo pipefail

# Self-check: runtime + gateway + delivery + common failure signals
# Output is intentionally short; designed for frequent runs.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="/tmp/openclaw/openclaw-$(date +%F).log"

echo "== openclaw gateway status =="
openclaw gateway status || true

echo

echo "== openclaw status (sessions + delivery signals) =="
openclaw status | sed -n '1,140p' || true

echo

echo "== cron list =="
openclaw cron list || true

echo

echo "== recent WARN/ERROR (last 200 lines) =="
if [[ -f "$LOG_FILE" ]]; then
  tail -n 200 "$LOG_FILE" | grep -E 'WARN|ERROR|embedded run agent end|delivery-recovery|sendMessage' || true
else
  echo "log file not found: $LOG_FILE"
fi

echo

echo "== env sanity =="
command -v python3 >/dev/null && echo "python3: yes" || echo "python3: no"
command -v python  >/dev/null && echo "python: yes"  || echo "python: no"
