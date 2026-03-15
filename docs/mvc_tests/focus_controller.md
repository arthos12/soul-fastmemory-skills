# MVC Test: dynamic focus controller

## Goal
Focus is computed and applied to idle lanes (freeze non-focus lanes).

## Steps
```bash
python3 scripts/req_latest.py >/dev/null
python3 scripts/req_focus.py
cat tasks/REQUIREMENTS_FOCUS.json
bash scripts/self_repair_idle.sh
python3 - <<'PY'
import json
q=json.load(open('tasks/IDLE_QUEUE.json','r',encoding='utf-8'))
print([(l['id'],l.get('enabled')) for l in q.get('lanes',[])])
PY
```

## Pass
- REQUIREMENTS_FOCUS.json exists with `allowedLanes`
- IDLE_QUEUE enables only allowed lanes
