# Idle Progress Audit Result — 2026-03-14

## Audit target
检查当前“空闲时主动推进任务”的能力，判断是否真的形成工作闭环。

## Result summary
总体判断：**部分通过，但仍未达标**。

## 1. Mainline continuity
- Pass (partial)
- Evidence:
  - `TASKS.md` 有明确主线：`soul-booster 持续开发与验收`。
  - `LAST_SESSION.md` 与 `SESSION_HANDOFF.md` 已写明当前主线、当前步骤、下一步。
  - 规则层已明确“回复不是终点”“空闲窗口继续推进”。
- Remaining weakness:
  - 还缺一次真实 `/new` + `加载数据` 验收，证明新 session 后仍能自动恢复这条主线。

## 2. Recovery-layer support
- Pass (partial)
- Evidence:
  - `LAST_SESSION.md` 已有 `Saved At`、主线、下一步。
  - `SESSION_HANDOFF.md` 已有 `Saved At`、主线、下一步。
  - 恢复协议已补入“恢复 autonomy / post-reply continuation”。
- Remaining weakness:
  - 目前是刚回填后的状态，还未证明小时级保存会持续稳定刷新。

## 3. Boundary discipline
- Pass (provisional)
- Evidence:
  - 当前推进内容都在安全边界内：文档修复、规则补强、任务板更新、恢复链路完善。
  - 没有越过权限/破坏性边界。
- Remaining weakness:
  - 还需要持续验证是否会“等太早”或“问太宽”。

## 4. Useful idle action quality
- Pass (partial)
- Evidence:
  - 最近空闲推进动作都直接服务主线：恢复链路、保存链路、审计规范、理解/逻辑升级闭环。
  - 不是无关清理，也不是纯记录无前进。
- Remaining weakness:
  - 还没形成固定的 idle-action checklist。
  - 还没接入 heartbeat / cron 触发方案。

## Final judgment
当前能力状态：**规则层已成型，恢复层已补齐一部分，触发层与真实验收仍不足。**

## Dominant failure category
按 `logic_understanding_upgrade_loop.md` 分型：
- 主失败类型不是“理解失败”
- 也不是“执行完全失败”
- **主失败类型是：save / recovery failure + partial rule adoption failure**

## Root-cause chain
- Problem: session 切换后“空闲主动推进”能力不稳定显现
- Root cause:
  1. 该能力长期只停留在规则层 / daily log
  2. 快恢复层缺失或未稳定刷新
  3. 没有真实触发与验收闭环
- Intervention:
  1. 回填 `LAST_SESSION.md` / `SESSION_HANDOFF.md`
  2. 给快恢复层加入 `Saved At`
  3. 把恢复协议补成恢复工作状态，而不只是恢复文本
  4. 新增空闲推进审计规范
- Expected improvement:
  - 新 session 更容易恢复“主线持续推进 / 空闲继续推进”的工作态
  - 用户不需要再次训练同一条能力

## Next actions
1. 做一次 `/new` + `加载数据` 验收
2. 固定 idle-action checklist
3. 设计 heartbeat / cron 触发方案
4. 观察 `Saved At` 是否能在后续小时级保存中稳定刷新
