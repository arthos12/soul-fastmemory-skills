#!/usr/bin/env bash
set -euo pipefail

# Reliable timed report via system-event routed to MAIN session.
# Usage: bash scripts/schedule_report_system_event.sh 30s

WHEN="${1:?need duration like 30s, 20m}"
RID="sev_$(date -u +%Y%m%dT%H%M%SZ)"

openclaw cron add --name "system_report_${RID}" \
  --description "System-event timed S/A ratio report" \
  --session main --system-event "REQ_RATIO_REPORT ${RID}" \
  --at "$WHEN" --delete-after-run >/dev/null

echo "$RID"
