# MVC Test: polymarket_batch

## Goal
One command generates a complete training batch (source -> filtered -> predictions -> score).

## Steps
```bash
bash scripts/polymarket_batch.sh --limit 80 --pick 30 --pred 20 --tag batchX
```

## Pass
- Prints OK and 4 file paths
- `data/polymarket/predictions_<date>_batchX_v1.jsonl` has >=20 lines
- `data/polymarket/score_<date>_batchX_v1.json` exists
