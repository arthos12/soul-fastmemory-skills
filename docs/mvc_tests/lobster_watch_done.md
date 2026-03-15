# MVC Test: lobster_watch (done)

## Goal
One command fetches Lobster token metrics and writes a snapshot to disk.

## Steps
```bash
bash scripts/lobster_watch.sh
```

## Pass
- Prints one-line summary starting with `LOBSTER`
- Appends to `data/lobster/lobster_snapshots.jsonl`
- Updates `data/lobster/lobster_latest.json`
