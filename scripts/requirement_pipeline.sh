#!/usr/bin/env bash
set -euo pipefail

# Requirement pipeline: sync backlog -> triage -> dedupe -> delivery ratio report

cd /root/.openclaw/workspace

python3 scripts/req_sync_backlog.py >/dev/null || true
python3 scripts/req_triage.py --limit 50 >/dev/null || true
python3 scripts/req_sync_backlog_status.py >/dev/null 2>&1 || true
python3 scripts/req_dedupe.py >/dev/null
python3 scripts/delivery_ratio_report_v2.py
