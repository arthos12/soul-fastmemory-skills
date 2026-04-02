# LLM Multi-Auth Router Plan (2026-03-16)

## Goal
Reduce provider/auth stalls by routing across multiple authorized slots (Gemini/OpenAI) when a slot is quota-limited or temporarily unavailable.

## Current skeleton
- Script: `scripts/llm-router.sh`
- Current default slot order:
  1. `gemini-a`
  2. `gemini-b`
  3. `openai-a`
  4. `openai-b`

## Slot types
### Gemini slots
Use isolated Gemini CLI browser OAuth state directories:
- `~/.gemini-a/`
- `~/.gemini-b/`

### OpenAI slots
Scaffolded as env files for now:
- `~/.config/openai-a.env`
- `~/.config/openai-b.env`

## Routing rule
1. Try slots in configured order.
2. If a slot fails with retryable/quota-like errors (quota, rate limit, 429, resource exhausted, temporary capacity), move to next slot.
3. If a slot fails with non-retryable errors (bad command, malformed request, missing binary, etc.), stop and report.
4. If all slots are exhausted, fail with summary.

## Why
This reduces the chance of the agent appearing stuck when one authorization is exhausted.

## Important boundaries
- Do not print secrets or raw credentials.
- Keep provider profiles isolated.
- Retry only on clearly retryable capacity/quota/auth-exhaustion style errors.
- Non-retryable failures should surface immediately for debugging.

## Next steps
1. Preserve current Gemini login as `~/.gemini-a/`.
2. Create second Gemini login as `~/.gemini-b/`.
3. If OpenAI multi-auth is needed, prepare `openai-a.env` and `openai-b.env` in a compatible CLI format.
4. Later add cooldown/memory of recently failed slots to avoid thrashing.
