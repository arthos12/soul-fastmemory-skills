#!/usr/bin/env bash
set -euo pipefail

# Schedule a timed requirement ratio report with a backup delivery.
# Usage: bash scripts/schedule_report.sh 20m

WHEN="${1:?need duration like 20m}"
CHAT="telegram:7628098396"
RID="rep_$(date -u +%Y%m%dT%H%M%SZ)"

# Primary
openclaw cron add --name "report_${RID}" \
  --description "Primary timed S/A ratio report" \
  --agent main --at "$WHEN" --delete-after-run --announce --to "$CHAT" \
  --message "用exec运行：cd /root/.openclaw/workspace && python3 scripts/req_latest.py >/dev/null 2>&1 || true; python3 scripts/req_ratio_snapshot.py --report-id ${RID}。只发这一行输出。" \
  --timeout-seconds 120 >/dev/null

# Backup after +3m
openclaw cron add --name "report_${RID}_backup" \
  --description "Backup timed S/A ratio report" \
  --agent main --at "${WHEN%m}m" --delete-after-run --announce --to "$CHAT" \
  --message "用exec运行：cd /root/.openclaw/workspace && if grep -q '${RID}' data/efficiency/report_marks.jsonl 2>/dev/null; then echo 'backup: primary already delivered'; else python3 scripts/req_latest.py >/dev/null 2>&1 || true; python3 scripts/req_ratio_snapshot.py --report-id ${RID}; fi" \
  --timeout-seconds 120 >/dev/null

echo "$RID"
