#!/usr/bin/env bash
set -euo pipefail

# Gemini dual-profile router (browser OAuth state based)
# Usage:
#   scripts/gemini-router.sh "your prompt"
#   scripts/gemini-router.sh --model gemini-2.5-pro "your prompt"
#
# Profiles expected:
#   ~/.gemini-a/
#   ~/.gemini-b/
#
# Strategy:
#   try A -> if quota/rate-limit/exhausted style error -> try B -> otherwise fail

PROFILE_A="${GEMINI_PROFILE_A:-$HOME/.gemini-a}"
PROFILE_B="${GEMINI_PROFILE_B:-$HOME/.gemini-b}"
MODEL_ARGS=()
PASS_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL_ARGS+=("$1" "${2:-}")
      shift 2
      ;;
    *)
      PASS_ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#PASS_ARGS[@]} -eq 0 ]]; then
  echo "usage: $0 [--model MODEL] \"prompt\"" >&2
  exit 2
fi

run_with_profile() {
  local profile="$1"
  local tmp_home
  tmp_home="$(mktemp -d)"
  trap 'rm -rf "$tmp_home"' RETURN
  mkdir -p "$tmp_home"
  if [[ -d "$profile" ]]; then
    cp -a "$profile" "$tmp_home/.gemini"
  fi
  HOME="$tmp_home" gemini "${MODEL_ARGS[@]}" "${PASS_ARGS[@]}" 2>&1
}

is_quota_error() {
  grep -Eiq 'quota|rate limit|too many requests|resource exhausted|exceeded|429'
}

OUT_A=""
set +e
OUT_A="$(run_with_profile "$PROFILE_A")"
RC_A=$?
set -e
if [[ $RC_A -eq 0 ]]; then
  printf '%s\n' "$OUT_A"
  exit 0
fi

if printf '%s' "$OUT_A" | is_quota_error; then
  OUT_B=""
  set +e
  OUT_B="$(run_with_profile "$PROFILE_B")"
  RC_B=$?
  set -e
  if [[ $RC_B -eq 0 ]]; then
    printf '%s\n' "$OUT_B"
    exit 0
  fi
  printf 'A failed with quota-like error, B also failed.\n--- A ---\n%s\n--- B ---\n%s\n' "$OUT_A" "$OUT_B" >&2
  exit 1
fi

printf '%s\n' "$OUT_A" >&2
exit "$RC_A"
