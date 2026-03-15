#!/usr/bin/env bash
set -euo pipefail

# A small default parallel validation pack (lane2).
# Runs a few key validations concurrently.

cd /root/.openclaw/workspace

# Only validate when something changed (avoid repeated no-op validations)
if bash scripts/changed_since_last_validate.sh; then
  python3 scripts/parallel_validate.py \
    --cmd "python3 scripts/req_latest.py" \
    --cmd "python3 scripts/delivery_ratio_report_v2.py" \
    --cmd "python3 scripts/efficiency_report_4nums.py --last-n 20"
else
  echo "SKIP_VALIDATE (no changes)"
fi
