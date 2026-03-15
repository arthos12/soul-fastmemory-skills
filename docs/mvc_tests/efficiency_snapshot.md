# MVC Test: efficiency_snapshot

## Goal
One command prints a human-first efficiency snapshot (concurrency, utilization, idle, completion ratio).

## Steps
```bash
python3 scripts/efficiency_snapshot.py --minutes 30
```

## Pass
- Outputs one line with: 并发/利用率/done增量/完成占比
