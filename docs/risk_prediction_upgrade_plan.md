# Risk Prediction Upgrade Plan

## Goal
针对当前“预测能力偏浅、对副作用/中断/退化/坏情况可执行性预判不足”的问题，建立一套可直接执行的升级方案。

## Current weakness
当前主要短板不是完全没有预判，而是：
1. 会写前瞻规则，但执行前不够自然地先扫风险
2. 对 session 关闭、数据丢失、恢复失败、能力退化的风险预判不足
3. 对账号限流、provider 错误、上下文截断等客观风险，缺少默认降级思维
4. 会想到“任务能不能做”，但还不够先问“坏情况来了还做不做得下去”

## Upgrade target
把预测能力升级为默认执行前脑回路：
- 先识别主人当前处境与客观风险
- 再把风险转成可执行需求
- 再补保存 / 恢复 / fallback / 降级路径
- 最后检查坏情况能否继续执行

## Execution plan
### Phase 1: rule hardening
- 新增 `skills/soul-booster/references/risk_predictive_execution.md`
- 把“现状识别 → 风险前置 → 风险转需求 → 落地防护 → 坏情况可执行性检查”写成固定链路

### Phase 2: task sync
- 写入 `TASKS.md`，把该能力列为当前主线补强项
- 写入 `LAST_SESSION.md` / `SESSION_HANDOFF.md`，让下次恢复能直接带出该升级方向
- 写入 daily memory，记录本轮问题来源与修复动作

### Phase 3: runtime adoption
- 后续处理重要方案、恢复链路、长任务、迁移任务时，默认先做最小风险扫描
- 优先检查：session 中断 / 恢复失败 / 限流 / 上下文截断 / 依赖不足 / fallback 缺失

## Acceptance
升级完成至少要达到：
- 不再只做事后复盘，而是在执行前就补风险位
- 能把主人问题里的隐含风险翻译成需求并落地
- 给出的方案在坏情况发生后仍尽量可执行
- 保存/恢复被提升为默认防风险动作，而不是补充动作
