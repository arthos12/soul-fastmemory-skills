# Self-Healing (Minimal, Behavior-Level)

## Goal
Prevent "silent failure" (no reply) and reduce recovery time after gateway/model/tool errors.

## Hard Rules
1. **No-silence ACK**: before any action likely to take >5–10s, send 1-line ACK (in chat). If a failure occurs (timeout/400/restart), send 1-line status + next step.
2. **After restart = self-check**: whenever gateway/model is restarted/switched, immediately run a self-check and confirm delivery is working.
3. **Tool failure = switch path**: on 403/CF challenge/API failure, immediately switch to alternate path (API-first, then browser) instead of explaining.
4. **One-shot timers only**: if user requests "in 1h tell me", create a one-shot cron (`--at +1h --delete-after-run`). Do not create recurring reports unless explicitly requested.

## Self-check Command
Run (local):
- `scripts/self_check.sh`

Expected outputs to inspect:
- gateway RPC probe ok
- sessions model correct
- delivery-recovery/telegram send ok
- recent WARN/ERROR contains no repeating 400/timeout loop

## Typical Fixes
- If `python` missing: use `python3` explicitly (do not assume `python`).
- If embedded run returns 400: retry once after short delay; if repeats, switch model or isolate session.
