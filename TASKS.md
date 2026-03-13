# TASKS.md

## skill-building
- [ ] **money-maker 初版落地**：完成本地私用赚钱 skill 的骨架、判断框架、执行入口与后续迭代方向。 (In Progress)
- [ ] **money-maker 主动发现模块**：补入主动分析赚钱机会/方向、学习补全、推理筛选能力。 (In Progress)
- [ ] **money-maker 边界清理**：确保只保留赚钱问题相关的学习/逻辑推理能力，不混入 soul 底层运行能力。 (In Progress)

## Active Goals

### 1. soul-booster 持续开发与验收 (主线)
- Status: testing_now
- Idle mandate: Jim 已明确授权空闲期自主推进，并优先检查“已提出但未真正实现”的需求，再继续补齐与验收。
- Goal: 大幅提高理解能力，理解主人的目标和需求，把关键需求与任务记住且后续不忘；持续提高逻辑能力、响应能力，并在空闲/空档期主动思考和推进任务目标。
- Current Sub-tasks:
  - [x] **并入自我运维规则**：已建立 `references/operational_logic.md` 并更新 `SKILL.md`。 (Completed)
  - [x] **强化目标转译逻辑**：已将“目标→任务化→持续推进→验证”设为底层工作流。 (Completed)
  - [ ] **覆盖检查**：对照 `references/acceptance_checklist.md` 检查 soul 是否已覆盖今天的核心需求与限定条件。
  - [ ] **结果验收汇报**：向主人汇报覆盖检查与表现结果，由主人验证是否真的“更智能、更主动”了。
  - [x] **逻辑/理解升级复测**：已完成第一轮分型与因果链复测，结果见 `docs/logic_understanding_retest_2026-03-14.md`。 (Completed)
  - [ ] **漏项回捞整理**：把本轮检查中未明确写硬的需求再次整理并补入需求总表/交付标准。
  - [x] **补入风险预测型执行**：已新增 `references/risk_predictive_execution.md` 与 `docs/risk_prediction_upgrade_plan.md`，补强对中断/退化/限流/坏情况不可执行的前置预判能力。 (Completed)
  - [x] **补入持续生效规则**：已整理 `references/persistence_rules.md`。 (Completed)
  - [x] **补入行为级检查清单**：已整理 `references/behavior_checklist.md`。 (Completed)
  - [x] **补入需求-抽象-执行对齐规则**：已整理 `references/alignment_rules.md` 并写入长期记忆。 (Completed)
  - [x] **补入规则层原则**：已整理 `references/rule_layer_principles.md`，明确规则层少而硬、不能乱/杂/臃肿。 (Completed)
  - [x] **补入思考能力底层原则**：已整理 `references/thinking_foundation.md`，明确思考能力做底层并模仿人脑。 (Completed)
  - [x] **补入思考能力子能力结构**：已整理 `references/thinking_capabilities.md`，补入判断/决策/纠偏/复盘等关键子能力。 (Completed)
  - [x] **补入低互动目标推进规则**：已整理 `references/low_interaction_execution.md`，明确目标明确时低互动、自主推进、快速达成结果。 (Completed)
  - [x] **补入最终方案生成规则**：已整理 `references/final_plan_generation.md`，并挂接到 `SKILL.md` / `MEMORY.md`。 (Completed)
  - [x] **补入行为压实最小规则**：已整理 `references/behavior_execution_minimum.md`，明确先快答/先抓目标/确认后马上做。 (Completed)
  - [x] **补入确认方案执行闭环**：已整理 `references/confirmed_plan_execution_loop.md`，明确锁定基线→完整执行→逻辑复查→轻量测试→交付结果。 (Completed)
  - [x] **补入流程层最小骨架**：已整理 `references/process_layer_minimum.md`，固定为目标→方案→确认→执行→验收。 (Completed)
  - [x] **补入执行层最小动作**：已整理 `references/execution_layer_minimum.md`，固定为确认后立即启动、关键步骤优先、必要汇报、结果后说明、最后验收。 (Completed)
  - [x] **补入需求捕获规则**：关键需求/任务先写入，重复和非任务内容可不写。 (Completed)
  - [x] **归纳需求总表**：已整理 `references/requirement_summary.md`。 (Completed)
  - [x] **补入速度优化规则**：已整理 `references/speed_optimization.md` 并写入执行法。 (Completed)
  - [x] **提炼核心运行规则**：已整理 `references/core_runtime_rules.md`，用于轻量化提速。 (Completed)
- Done when: 主人认可理解能力已提升，能自动推进并验证达标。

### 2. fast-memory 持续开发与验收
- Status: testing_now
- Goal: 解决高信息量互动后 new session 丢失关键内容的问题，实现准确落盘与恢复。
- Current Sub-tasks:
  - [x] 已完成一次真实“现在保存 session”执行：本轮已主动刷新 `LAST_SESSION.md` / `SESSION_HANDOFF.md`，并写入本 session 新增需求。后续仍需补做严格恢复验收。 (Completed)
  - [ ] 做一次 new session 恢复测试
  - [x] 已补固定验收文档：`docs/new_session_recovery_acceptance.md`，用于真实 `/new` + `加载数据` 验收。 (Completed)
  - [ ] 依据 `docs/session_restore_recovery_plan.md` + `docs/new_session_recovery_acceptance.md` 做一次 `/new` + `加载数据` 验收，检查主线恢复 / 行为恢复 / 能力恢复。
- Done when: new 恢复后不丢主线、不丢规则、不丢断点。

### 3. 空闲时主动维护能力增强
- Status: in_progress
- Goal: 提升 agent 在空闲 / 间隙 / 被触发时主动推进项目与维护的能力
- Current focus:
  - [x] 新增 `SELF_OPERATIONS.md`
  - [x] 写入前台优先 / 后台推进 / 防死机 / 恢复规则
  - [x] 把空闲动作清单固定到可执行规则中：`docs/idle_action_checklist.md`。 (Completed)
  - [x] 已设计 heartbeat / cron 触发式维护方案：`docs/heartbeat_cron_maintenance_plan.md`。 (Completed)
  - [x] 把“大模型调用最小化 / token 压缩”写进空闲推进与默认运行策略，避免空闲维护本身反而高耗 token。 (Completed)
  - [x] 固定“本地优先空闲维护”清单：任务推进 / 逻辑升级 / 理解升级 / 未执行需求检查 / 炎症排查。 (Completed)
  - [x] 固定“自我执行范围”清单：空闲推进完成度 / 自我升级思考能力 / 检查未执行与未保存需求。 (Completed)
  - [x] 固定“碎片化需求处理”流程：记录 → 分型 → 判断必要性 → 真实执行 / 停车 / 丢弃。 (Completed)
  - [x] 固定 token 优化方案：`docs/token_optimization_strategy.md` + `interaction_compression.md` + `context_budgeting.md`。 (Completed)
  - [x] 固定 light / mid / heavy 回复长度与上下文预算表：`response_mode_budgeting.md`。 (Completed)
  - [ ] 做一次“短空闲推进能力”测试记录
  - [ ] 补齐主动推进/空闲推进的恢复闭环：确保该能力同时写入规则层、快恢复层、触发层，并经 `/new` + `加载数据` 验收。
  - [x] 已补“预判/预测能力专项保存检查”文档：`docs/foresight_persistence_audit.md`。 (Completed)
  - [x] 依据 `skills/soul-booster/references/idle_progress_audit.md` 做一次空闲推进能力审计，结果见 `docs/idle_progress_audit_result_2026-03-14.md`。 (Completed)
- Done when:
  - 有固定任务板
  - 有固定空闲动作清单
  - 有触发式维护方案
  - 测试结果已记录

## Parking Lot
- openclaw gateway restart SIGTERM 根因排查
- Git 身份配置与 commit
- Git 私有远端备份决策
- Notion 自动同步规则

## Rule
- 目标未完成，不移出。
- 达标并验收通过后，才能移到完成区。
- 每次新消息到来前，先检查当前主线 / 支线 / 停车区，不按单句问答模式漂移。
- 每次回复后，应立即恢复主线下一步推进；回复本身不算任务完成。
