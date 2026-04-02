#!/usr/bin/env bash
set -euo pipefail

# Multi-provider LLM router skeleton
# Goal: reduce stalls by trying multiple provider/profile authorizations.
# Current implementation supports Gemini CLI profiles first; OpenAI slots are scaffolded.
#
# Usage:
#   scripts/llm-router.sh --provider-order gemini-a,gemini-b "your prompt"
#   scripts/llm-router.sh "your prompt"
#
# Env vars (optional):
#   GEMINI_PROFILE_A=~/.gemini-a
#   GEMINI_PROFILE_B=~/.gemini-b
#   OPENAI_PROFILE_A=~/.config/openai-a.env
#   OPENAI_PROFILE_B=~/.config/openai-b.env

GEMINI_PROFILE_A="${GEMINI_PROFILE_A:-$HOME/.gemini-a}"
GEMINI_PROFILE_B="${GEMINI_PROFILE_B:-$HOME/.gemini-b}"
OPENAI_PROFILE_A="${OPENAI_PROFILE_A:-$HOME/.config/openai-a.env}"
OPENAI_PROFILE_B="${OPENAI_PROFILE_B:-$HOME/.config/openai-b.env}"
ORDER="${LLM_ROUTER_ORDER:-gemini-a,gemini-b,openai-a,openai-b}"
ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --provider-order)
      ORDER="$2"
      shift 2
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "usage: $0 [--provider-order a,b,...] \"prompt\"" >&2
  exit 2
fi

is_retryable_error() {
  grep -Eiq 'quota|rate limit|too many requests|resource exhausted|exceeded|429|capacity|temporarily unavailable|try again later'
}

run_gemini_profile() {
  local profile="$1"
  local tmp_home
  tmp_home="$(mktemp -d)"
  mkdir -p "$tmp_home"
  if [[ -d "$profile" ]]; then
    cp -a "$profile" "$tmp_home/.gemini"
  fi
  set +e
  HOME="$tmp_home" gemini "${ARGS[@]}" 2>&1
  local rc=$?
  set -e
  rm -rf "$tmp_home"
  return $rc
}

run_openai_profile() {
  local envfile="$1"
  if [[ ! -f "$envfile" ]]; then
    echo "missing openai profile env: $envfile"
    return 9
  fi
  set -a
  # shellcheck disable=SC1090
  source "$envfile"
  set +a
  if ! command -v openai >/dev/null 2>&1; then
    echo "openai CLI not installed"
    return 10
  fi
  openai api chat.completions.create -m gpt-4o-mini -g user "${ARGS[*]}" 2>&1
}

try_slot() {
  local slot="$1"
  case "$slot" in
    gemini-a) run_gemini_profile "$GEMINI_PROFILE_A" ;;
    gemini-b) run_gemini_profile "$GEMINI_PROFILE_B" ;;
    openai-a) run_openai_profile "$OPENAI_PROFILE_A" ;;
    openai-b) run_openai_profile "$OPENAI_PROFILE_B" ;;
    *) echo "unknown slot: $slot"; return 8 ;;
  esac
}

IFS=',' read -r -a slots <<< "$ORDER"
last_err=""
for slot in "${slots[@]}"; do
  set +e
  out="$(try_slot "$slot")"
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    printf '%s\n' "$out"
    exit 0
  fi
  if printf '%s' "$out" | is_retryable_error; then
    last_err+=$'\n--- '
    last_err+="$slot"
    last_err+=$' ---\n'
    last_err+="$out"
    continue
  fi
  printf 'slot %s failed with non-retryable error:\n%s\n' "$slot" "$out" >&2
  exit "$rc"
done

printf 'all configured slots exhausted or retryable-failed:%s\n' "$last_err" >&2
exit 1
