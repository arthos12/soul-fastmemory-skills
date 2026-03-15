# MVC Test: req_sync_backlog_status

## Goal
Structured triaged status matches DELIVERY_BACKLOG ([m]/[x]).

## Steps
```bash
python3 scripts/req_sync_backlog_status.py
python3 scripts/req_latest.py >/dev/null
python3 scripts/delivery_ratio_report_v2.py | head -n 20
```

## Pass
- `req_sync_backlog_status.py` reports updated>=0 without error
- `delivery_ratio_report_v2` no longer shows backlog_* items with status contradicting DELIVERY_BACKLOG
