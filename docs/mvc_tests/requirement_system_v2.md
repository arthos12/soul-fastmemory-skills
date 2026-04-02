# MVC Test: requirement system v2

## Goal
Capture -> triage -> report requirements without relying on chat context.

## Steps
```bash
python3 scripts/req_add.py --text "效率提升：空闲不浪费" --priority P0
python3 scripts/req_triage.py --limit 5
python3 scripts/req_report.py
```

## Pass
- Inbox jsonl appended
- Triaged jsonl appended with truth/importance/type
- Report prints counts and top pending
