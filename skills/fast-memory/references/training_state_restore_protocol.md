# Training-state restore protocol ("加载数据")

Goal: restore the agent into the **trained operating state**, not merely recall facts.

## Trigger
- User says: `加载数据` / `加载记忆` / `恢复数据` / `恢复记忆` / `先加载一下` / `你先读一下`

## Restore order (default)
1. `LAST_SESSION.md` (fast-recovery main line)
2. `SESSION_HANDOFF.md` (rolling snapshot)
3. `MEMORY.md` (durable rules / user prefs)
4. `tasks/*` (especially `tasks/soul_skill_transfer.md`) + `TASKS.md` (task board)
5. `memory/YYYY-MM-DD.md` (today + yesterday only)

If any file is missing, skip it; do not block.

## Output format (must be short)
Return **only**:
- Saved-at timestamp(s) from fast-recovery layer if present
- Current topic / main line
- Current step
- Next step (single concrete action)
- Blocker / constraint (if any)
- Key files (max 5)
- Operating mode hint: `light|mid|heavy` (one word)

## Behavior constraints
- Frontstage-first: send a short restore summary quickly; do not do deep reading before the first visible reply.
- Truthfulness: if the question is about "current state", rely on live file reads (not cached chat text).
- Don’t drift into long explanations; restore state, then ask what to do next.
- Restore autonomy: when the active topic is a continuing mainline, recover the expectation that the agent should keep pushing the task during safe idle windows instead of waiting for renewed interaction.
- Restore post-reply continuation: the working rule is “reply is not the end; after replying, resume the mainline next step.”
