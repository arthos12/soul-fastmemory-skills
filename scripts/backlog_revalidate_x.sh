#!/usr/bin/env bash
set -euo pipefail

# Re-validate [x] backlog items: if their artifact command is stub/invalid, downgrade to [m].
# Heuristic: expects `artifacts=scripts/<slug>.sh` in the line.

cd /root/.openclaw/workspace
BACKLOG="tasks/DELIVERY_BACKLOG.md"
TMP=$(mktemp)
changed=0

while IFS= read -r line; do
  if [[ "$line" =~ ^-\ \[x\]\ ([a-z0-9_\-]+)\ .*artifacts=([^ ]+) ]]; then
    slug="${BASH_REMATCH[1]}"
    artifacts="${BASH_REMATCH[2]}"
    # Only handle single script artifact like scripts/<slug>.sh
    if [[ "$artifacts" == scripts/*.sh ]]; then
      cmd="bash $artifacts"
      if ! bash scripts/verify_artifact_output.sh "$cmd" "/tmp/reval_${slug}.out" >/dev/null 2>&1; then
        # downgrade
        line="${line/\[x\]/[m]}"
        line+="  # downgraded_from_x=stub_detected"
        changed=$((changed+1))
      fi
    fi
  fi
  echo "$line" >> "$TMP"
done < "$BACKLOG"

cat "$TMP" > "$BACKLOG"
rm -f "$TMP"

echo "DOWNGRADED $changed"
