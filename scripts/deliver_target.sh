#!/usr/bin/env bash
set -euo pipefail

# Deliver a locked target (preferred) or fall back to next MVC->DONE conversion.
# Target slug stored in tasks/DELIVERY_TARGET.txt (single line).

cd /root/.openclaw/workspace

TARGET_FILE="tasks/DELIVERY_TARGET.txt"
slug=""
if [[ -f "$TARGET_FILE" ]]; then
  slug=$(head -n 1 "$TARGET_FILE" | tr -d '\r' | xargs || true)
fi

# Skip A-share target (paused by user)
if [[ "$slug" == "a_share_data_demo" ]]; then
  slug=""
fi

# Auto-pick next [m] item (excluding A-share) if no valid target
if [[ -z "$slug" ]]; then
  slug=$(grep -nE '^- \[m\] [a-z0-9_\-]+' tasks/DELIVERY_BACKLOG.md | awk '{print $3}' | grep -v '^a_share_data_demo$' | head -n 1 || true)
  if [[ -n "$slug" ]]; then
    echo "$slug" > "$TARGET_FILE"
  fi
fi

if [[ -z "$slug" ]]; then
  echo "NO_TARGET"
  exit 0
fi

# Verify + mark done for that slug using the same rules as convert_next_mvc_to_done
verify_cmd=""
case "$slug" in
  requirement_intake_and_dedupe)
    verify_cmd="bash scripts/requirement_pipeline.sh";;
  delivery_ratio_report_v2)
    verify_cmd="python3 scripts/delivery_ratio_report_v2.py";;
  *)
    if [[ -f "scripts/${slug}.sh" ]]; then
      verify_cmd="bash scripts/${slug}.sh"
    elif [[ -f "scripts/${slug}.py" ]]; then
      verify_cmd="python3 scripts/${slug}.py"
    else
      echo "NO_VERIFY_CMD_FOR $slug"; exit 2
    fi
    ;;
esac

# must not be stub
bash scripts/verify_artifact_output.sh "$verify_cmd" "/tmp/deliver_target.${slug}.out"

# Now mark backlog line [m]->[x] for the slug (if present)
if grep -qE "^- \[m\] ${slug}\\b" tasks/DELIVERY_BACKLOG.md; then
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  tmp=$(mktemp)
  awk -v slug="$slug" -v now="$now" '
    $0 ~ "^- \\[m\\] "slug"(\\s|\\b|-)" {
      sub("\\[m\\]","[x]");
      # refresh done_at
      if ($0 ~ /done_at=/) {
        gsub(/done_at=[0-9TZ:\-]+/, "done_at=" now)
      } else {
        $0 = $0 "  # done_at=" now
      }
      # remove old downgraded marker if present
      gsub(/\s+# downgraded_from_x=stub_detected/, "")
      print $0;
      next
    }
    {print}
  ' tasks/DELIVERY_BACKLOG.md > "$tmp"
  cat "$tmp" > tasks/DELIVERY_BACKLOG.md
  rm -f "$tmp"
  echo "DONE_X $slug"
else
  echo "TARGET_OK_BUT_NOT_IN_BACKLOG $slug"
fi
