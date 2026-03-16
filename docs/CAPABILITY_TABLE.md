# CAPABILITY_TABLE.md

## Purpose
This file is the stable entrypoint for business-layer/system-layer capability auditing and calibration.
It is a system-level asset and must not be casually replaced or rewritten.

## Protection Rules
- Do not casually rewrite the whole table.
- Prefer append / calibrate / deprecate / mark stale / add acceptance criteria.
- If an old capability exists but is not surfacing, treat it as a recovery problem first, not as a reason to replace the table.
- Capability-table changes should preserve history of important capabilities and their status shifts.

## Current Canonical Audit File
- `docs/capability_check_and_calibration_2026-03-16.md`

## Minimum Fields For Capability Entries
- capability name
- layer/type
- current status: stable / weak / lost-partial / stale
- failure symptom
- calibration action
- acceptance signal

## Current Highest Priority Capability Risks
1. stable recovery and triggering of old abilities
2. root-problem locking before broad handling
3. explanation -> solution -> execution same-turn behavior
4. solution -> direct execution behavior
5. capability-table persistence across session switches

## Rule
If this table and a one-off audit differ, do not silently discard the old capability. First reconcile, then calibrate, then preserve.
