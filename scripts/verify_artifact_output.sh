#!/usr/bin/env bash
set -euo pipefail

# Verify that a command produced non-stub output.
# Fails if output contains obvious stub markers.

CMD="${1:?need command string}"
OUT_FILE="${2:-/tmp/verify_artifact_output.out}"

bash -lc "$CMD" >"$OUT_FILE" 2>&1 || { echo "VERIFY_FAIL: command failed"; exit 2; }

# Stub markers
if grep -qiE 'TODO: implement|TODO\b|not implemented|placeholder' "$OUT_FILE"; then
  echo "VERIFY_FAIL: stub output detected"
  exit 3
fi

# Must have some output
if [[ ! -s "$OUT_FILE" ]]; then
  echo "VERIFY_FAIL: empty output"
  exit 4
fi

echo "VERIFY_OK"
