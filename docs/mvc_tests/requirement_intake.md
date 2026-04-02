# MVC Test: requirement intake

## Goal
A single command can capture a raw requirement into DELIVERY_BACKLOG.

## Steps
```bash
bash scripts/requirement_intake.sh "test requirement: add X" P2
```

## Pass
- A new unchecked line appears under section `## P2` in `tasks/DELIVERY_BACKLOG.md`
