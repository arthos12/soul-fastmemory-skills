# MVC Test: model_audit_auto_log (done)

## Goal
One command appends a structured model/scene/metrics audit record locally.

## Steps
```bash
bash scripts/model_audit_auto_log.sh
```

## Pass
- Prints line starting with `MODEL_AUDIT`
- Appends one line to `data/model_audit/audit.jsonl`
