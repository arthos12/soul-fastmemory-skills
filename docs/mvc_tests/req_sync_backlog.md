# MVC Test: req_sync_backlog

## Goal
Sync DELIVERY_BACKLOG.md items into structured REQUIREMENTS jsonl.

## Steps
```bash
python3 scripts/req_sync_backlog.py
python3 scripts/req_report.py
```

## Pass
- `tasks/REQUIREMENTS_INBOX.jsonl` appended
- `tasks/REQUIREMENTS_TRIAGED.jsonl` appended
- report shows counts
