#!/usr/bin/env bash
set -euo pipefail

# Unified interface runner: run a capability script and log audit.
# Usage: scripts/run_cap.sh <capability-name> [args...]
# Example: scripts/run_cap.sh polymarket_batch --limit 80 --pick 30 --out-tag batch6

CAP="${1:?need capability name}"
shift || true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TS_UTC="$(date -u +%FT%TZ)"
AUDIT_DIR="data/model_audit"
AUDIT_FILE="$AUDIT_DIR/audit_log.jsonl"
mkdir -p "$AUDIT_DIR"

SCRIPT="scripts/${CAP}.sh"
if [[ ! -x "$SCRIPT" ]]; then
  echo "missing executable: $SCRIPT" >&2
  exit 2
fi

set +e
OUT=$($SCRIPT "$@" 2>&1)
CODE=$?
set -e

# Log
python3 - <<PY
import json, os, sys
rec={
  'ts': '${TS_UTC}',
  'capability': '${CAP}',
  'argv': ['${CAP}'] + ${json.dumps([])},
  'exitCode': ${CODE},
}
# argv detailed (best-effort):
rec['args']=sys.argv[1:]
rec['outputTail']='\n'.join(${json.dumps([])})
print(json.dumps(rec,ensure_ascii=False))
PY "$@" >> "$AUDIT_FILE"

# Print output for interactive runs
printf "%s\n" "$OUT"
exit $CODE
