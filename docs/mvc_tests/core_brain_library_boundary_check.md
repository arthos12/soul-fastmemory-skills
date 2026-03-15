# MVC Test: core brain library boundary check

## Goal
Ensure core brain libraries do not drift or mix boundaries.

## Run
```bash
bash scripts/check_core_brain_library_boundaries.sh
```

## Pass
- Prints `BOUNDARY_CHECK_OK`
- Fails if U-series mixes logic/prediction/runtime content
- Fails if constitution reference is missing from key files
