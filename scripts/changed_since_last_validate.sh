#!/usr/bin/env bash
set -euo pipefail

# Returns 0 (true) if meaningful files changed since last validation run.
# Uses a timestamp marker in data/validation/last_validate_ts.

cd /root/.openclaw/workspace
MARK_DIR="data/validation"
MARK="$MARK_DIR/last_validate_ts"
mkdir -p "$MARK_DIR"

last=0
if [[ -f "$MARK" ]]; then
  last=$(cat "$MARK" || echo 0)
fi
now=$(date -u +%s)

# check for changes in scripts/, tasks/DELIVERY_BACKLOG.md, data/* latest outputs
changed=$(find scripts tasks -maxdepth 2 -type f \( -name '*.sh' -o -name '*.py' -o -name 'DELIVERY_BACKLOG.md' -o -name 'REQUIREMENTS_TRIAGED.jsonl' -o -name 'requirements_latest.jsonl' \) -printf '%T@ %p\n' 2>/dev/null | awk -v last="$last" '$1>last {c++} END{print c+0}')

if [[ "$changed" -gt 0 ]]; then
  echo "$now" > "$MARK"
  exit 0
else
  exit 1
fi
