# Gemini Dual OAuth Router Plan (2026-03-16)

## Goal
Use two browser-OAuth Gemini CLI profiles and switch to profile B when profile A hits quota/rate-limit style failures.

## Assumed layout
- `~/.gemini-a/` : account A OAuth state
- `~/.gemini-b/` : account B OAuth state
- router script: `scripts/gemini-router.sh`

## Current status
- Current environment appears to use Gemini CLI browser OAuth login state.
- Existing Gemini state directory detected at `~/.gemini/`.

## Router behavior
1. Try profile A first.
2. If A succeeds, return result.
3. If A fails with quota/rate-limit/resource-exhausted/429 style error, try profile B.
4. If B succeeds, return result.
5. If B also fails, return both errors.
6. If A fails for non-quota reasons, do not switch; return A error directly.

## Why isolate profiles
Browser OAuth is usually persisted as local CLI state. The safest way to avoid account/session contamination is to keep separate local state directories, not one mixed state.

## Next setup step
1. Preserve current `~/.gemini/` as profile A by copying it to `~/.gemini-a/`.
2. Create/login profile B separately and store it as `~/.gemini-b/`.
3. Use `scripts/gemini-router.sh` for routed Gemini calls.

## Notes
- This is a minimal router skeleton, not yet a full persistent state manager.
- It currently copies the selected profile into a temporary HOME for each invocation to avoid touching the main default state.
- If Gemini CLI later exposes a cleaner config-dir flag/env, the router should switch to that.
