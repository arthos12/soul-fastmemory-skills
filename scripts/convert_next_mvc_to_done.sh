#!/usr/bin/env bash
set -euo pipefail

# Convert next [m] item in DELIVERY_BACKLOG.md to [x] after verifying its script runs.
# Heuristic: assumes the first token after checkbox is the slug and that a script exists at scripts/<slug>.sh.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKLOG="tasks/DELIVERY_BACKLOG.md"

line=$(grep -nE '^- \[m\] [a-z0-9_\-]+' "$BACKLOG" | head -n 1 || true)
if [[ -z "$line" ]]; then
  echo "NO_MVC"
  exit 0
fi

lnum=${line%%:*}
item=${line#*] }
slug=$(echo "$item" | awk '{print $1}')
slug=$(echo "$slug" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_\-]+/_/g; s/^_+|_+$//g')

# Map slug -> verification command + artifacts
verify_cmd=""
artifacts=""
case "$slug" in
  requirement_intake_and_dedupe)
    verify_cmd="bash scripts/requirement_pipeline.sh"
    artifacts="scripts/requirement_pipeline.sh,scripts/req_add.py,scripts/req_triage.py,scripts/req_sync_backlog.py,scripts/req_dedupe.py,data/requirements/dedupe_report.json"
    ;;
  delivery_ratio_report_v2)
    verify_cmd="python3 scripts/delivery_ratio_report_v2.py"
    artifacts="scripts/delivery_ratio_report_v2.py"
    ;;
  *)
    if [[ -f "scripts/${slug}.sh" ]]; then
      verify_cmd="bash scripts/${slug}.sh"
      artifacts="scripts/${slug}.sh"
    elif [[ -f "scripts/${slug}.py" ]]; then
      verify_cmd="python3 scripts/${slug}.py"
      artifacts="scripts/${slug}.py"
    else
      echo "NO_VERIFY_CMD_FOR $slug"
      exit 2
    fi
    ;;
esac

# Run verification (must exit 0)
bash scripts/verify_artifact_output.sh "$verify_cmd" /tmp/convert_next_mvc_to_done.${slug}.out

now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Mark line as [x] and append done_at only once
# Keep original line content, just swap [m] -> [x]
tmp=$(mktemp)
awk -v n="$lnum" -v now="$now" -v artifacts="$artifacts" '
  NR==n {
    sub("\\[m\\]","[x]");
    if ($0 !~ /done_at=/) {
      print $0 "  # done_at=" now " artifacts=" artifacts;
    } else {
      print $0;
    }
    next
  }
  {print}
' "$BACKLOG" > "$tmp"
cat "$tmp" > "$BACKLOG"
rm -f "$tmp"

echo "DONE_X $slug"
