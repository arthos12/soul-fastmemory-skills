#!/usr/bin/env bash
set -euo pipefail
OUTDIR="data/memory_compact"
mkdir -p "$OUTDIR"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

size_kb() { if [[ -f "$1" ]]; then du -k "$1" | awk '{print $1}'; else echo 0; fi }

mem_kb=$(size_kb MEMORY.md)
last_kb=$(size_kb LAST_SESSION.md)
hand_kb=$(size_kb SESSION_HANDOFF.md)

# latest daily log (if any)
latest_daily=$(ls -1t memory/*.md 2>/dev/null | head -n 1 || true)
if [[ -n "${latest_daily}" ]]; then daily_kb=$(size_kb "$latest_daily"); else daily_kb=0; fi

report=$(printf '{"ts":"%s","memory_kb":%s,"last_session_kb":%s,"handoff_kb":%s,"latest_daily":"%s","daily_kb":%s}' "$TS" "$mem_kb" "$last_kb" "$hand_kb" "${latest_daily:-}" "$daily_kb")
echo "$report" > "$OUTDIR/report.json"

touch "$OUTDIR/alerts.jsonl"

alert_if() {
  local name=$1 val=$2 thr=$3 file=$4
  if [[ $val -gt $thr ]]; then
    printf '{"ts":"%s","file":"%s","name":"%s","kb":%s,"threshold_kb":%s}' "$TS" "$file" "$name" "$val" "$thr" >> "$OUTDIR/alerts.jsonl"
    printf '\n' >> "$OUTDIR/alerts.jsonl"
  fi
}

alert_if "MEMORY" "$mem_kb" 40 "MEMORY.md"
alert_if "LAST_SESSION" "$last_kb" 25 "LAST_SESSION.md"
alert_if "SESSION_HANDOFF" "$hand_kb" 12 "SESSION_HANDOFF.md"
if [[ -n "${latest_daily}" ]]; then
  alert_if "DAILY" "$daily_kb" 20 "$latest_daily"
fi
