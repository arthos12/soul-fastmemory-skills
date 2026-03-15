#!/usr/bin/env bash
set -euo pipefail

# Self-repair for idle evolution: detect low effective output and auto-adjust queue.
# No messaging; writes a decision record.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

METRICS="data/efficiency/metrics.jsonl"
DECISIONS="data/efficiency/decisions.jsonl"
QUEUE="tasks/IDLE_QUEUE.json"
BACKLOG="tasks/DELIVERY_BACKLOG.md"

mkdir -p data/efficiency

# If no metrics yet, do nothing
if [[ ! -f "$METRICS" ]]; then
  exit 0
fi

last=$(tail -n 1 "$METRICS")

# Parse fields with python3 (safe even if fields absent)
read -r mvc scripts_changed backlog_pending backlog_mvc backlog_done <<<"$(python3 - <<'PY'
import json,sys
r=json.loads(sys.stdin.read() or '{}')
print(r.get('mvcCreated10m',0), r.get('scriptsChanged10m',0), r.get('backlogPending',0), r.get('backlogMVC',0), r.get('backlogDone',0))
PY
<<<"$last")"

# Dynamic focus controller (F0): compute allowed lanes and apply as execution-rights
python3 scripts/req_latest.py >/dev/null 2>&1 || true
python3 scripts/req_focus.py >/dev/null 2>&1 || true
FOCUS_FILE="tasks/REQUIREMENTS_FOCUS.json"
allowed_lanes=""
focus_reason=""
if [[ -f "$FOCUS_FILE" ]]; then
  read -r allowed_lanes focus_reason <<<"$(python3 - <<'PY'
import json
f='tasks/REQUIREMENTS_FOCUS.json'
j=json.load(open(f,'r',encoding='utf-8'))
print(','.join(j.get('allowedLanes',[])), j.get('reason',''))
PY
)"
fi

# Repair policy:
# 1) If there is any pending backlog, force delivery_first and disable P1/P2.
# 2) If no pending but lots of mvc (skeletons) and no done progress, keep P0 only.
# 3) Otherwise allow WIP=2 (P0+P1).

apply_disable_p1=false
reason=""

if [[ "$backlog_pending" -gt 0 ]]; then
  apply_disable_p1=true
  reason="pending_backlog_force_delivery_first"
elif [[ "$backlog_mvc" -gt 0 && "$backlog_done" -lt 2 && "$mvc" -eq 0 && "$scripts_changed" -eq 0 ]]; then
  apply_disable_p1=true
  reason="mvc_backlog_stalled_focus_on_delivery"
fi

if [[ "$apply_disable_p1" == true ]]; then
  # Disable P1/P2 by editing JSON with python
  python3 - <<'PY'
import json
p='tasks/IDLE_QUEUE.json'
q=json.load(open(p,'r',encoding='utf-8'))
for lane in q.get('lanes',[]):
    if lane.get('id') in ('P1_polymarket','P2_business'):
        lane['enabled']=False
q['priorityMode']='delivery_first'
json.dump(q, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
PY

  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"decision\":\"self_repair_disable_p1\",\"reason\":\"$reason\",\"focus_reason\":\"$focus_reason\",\"allowed\":\"$allowed_lanes\",\"verify\":\"python3 scripts/idle_dispatcher.py && tail -n 1 data/efficiency/metrics.jsonl\"}" >> "$DECISIONS"
else
  # Enable P1 (leave P2 off), keep delivery_first mode on
  python3 - <<'PY'
import json
p='tasks/IDLE_QUEUE.json'
q=json.load(open(p,'r',encoding='utf-8'))
for lane in q.get('lanes',[]):
    if lane.get('id')=='P1_polymarket':
        lane['enabled']=True
    if lane.get('id')=='P2_business':
        lane['enabled']=False
q['priorityMode']=q.get('priorityMode','delivery_first')
json.dump(q, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
PY

  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"decision\":\"self_repair_enable_p1\",\"reason\":\"ok\",\"focus_reason\":\"$focus_reason\",\"allowed\":\"$allowed_lanes\",\"verify\":\"python3 scripts/idle_dispatcher.py && tail -n 1 data/efficiency/metrics.jsonl\"}" >> "$DECISIONS"
fi

# Apply focus as final override (execution-rights gate)
# If focus exists, only lanes in allowedLanes are enabled.
if [[ -n "$allowed_lanes" ]]; then
  ALLOWED="$allowed_lanes" python3 - <<'PY'
import json, os
allowed=set([x for x in (os.environ.get('ALLOWED','').split(',')) if x])
p='tasks/IDLE_QUEUE.json'
q=json.load(open(p,'r',encoding='utf-8'))
for lane in q.get('lanes',[]):
    lid=lane.get('id')
    if lid in allowed:
        lane['enabled']=True
    else:
        lane['enabled']=False
json.dump(q, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
PY
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"decision\":\"focus_override\",\"focus_reason\":\"$focus_reason\",\"allowed\":\"$allowed_lanes\"}" >> "$DECISIONS"
fi
