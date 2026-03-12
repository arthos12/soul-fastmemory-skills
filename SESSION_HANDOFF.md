# SESSION_HANDOFF.md

## Current Memory System Baseline

### Agreed Rules
- Jim 说“结束 session”，默认含义就是：立即做 session 收尾、提炼关键信息并落盘保存。
- Jim 若表达“这轮先到这 / 先收尾 / 你去记一下 / 保存一下这次内容”等类似意图，也应按 session 结束处理。
- Jim 若表达“加载记忆 / 加载数据 / 恢复记忆 / 恢复数据 / 先加载一下 / 你先读一下”等类似意图，也应直接执行上下文恢复与资料读取。
- 所有触发规则以语义理解为主，不要求死板词条匹配。

### Storage Rules
- 过程性信息 → `memory/YYYY-MM-DD.md`
- 长期有效偏好/原则 → `MEMORY.md`
- 可恢复执行断点 → `SESSION_HANDOFF.md` / `LAST_SESSION.md` / checkpoint

## Current State (Latest)
- 主线：**fast-memory 动态保存（incremental save）+ 自动收尾落盘** 已写入 skill；下一步做一次真实 `/new` 验收，确认自动落盘与恢复命中。
- 已确认（来自既有记录）：
  - `LAST_SESSION.md` 作为默认 fast-recovery 快照层（不再可选）
  - 缺少 `LAST_SESSION.md` 视为 save loop incomplete
  - workspace / skills-active / skills-installed 三处已同步
  - `openclaw skills info fast-memory` → `Ready`
- 待诊断：`openclaw gateway restart` SIGTERM 中断。

## Next Step
1) **动态保存验收**：我们推进一小段工作 → 我在阶段结束处主动 quick-save → Jim 直接 `/new` → 我新会话按 `LAST_SESSION.md`/`SESSION_HANDOFF.md` 恢复。
2) 若要排查 SIGTERM：贴出 restart 完整输出或 systemd/journal 片段。
