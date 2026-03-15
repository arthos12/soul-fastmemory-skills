# MVC Test: convert_next_mvc_to_done

## Goal
When backlog has [m] items, we can convert one to [x] with a runnable script and evidence.

## Steps
```bash
bash scripts/convert_next_mvc_to_done.sh
```

## Pass
- One line in `tasks/DELIVERY_BACKLOG.md` changes from `[m]` to `[x]`
- Line contains `done_at=` and `artifacts=`

## Extra rule
- [x] verification must fail on stub output (TODO/placeholder).
