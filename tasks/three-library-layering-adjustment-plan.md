# 三库分层调整方案（2026-03-16）

## 目标
在不直接修改三库底层真模型内容的前提下，收紧三库边界，剥离伪底层模型，避免调度层、运行协议层、输出风格层、应用工具层继续伪装成底层真理模型。

## 核心原则
1. 三库底层只允许“真理级底层模型”进入。
2. 其他层（调度/运行/风格/应用）不得进入三库底层。
3. 先做分层与入口重构，不先删文件，不先重写底层内容。
4. 新增内容默认先进候选层，不直接进入三库底层。

## 五层结构
### 1. 真底层（三库）
- 理解真模型：如抓关键变量、结构映射、语义解构、动态理解更新、深层意图识别
- 逻辑真模型：如表征、假设空间、约束一致性、分叉预判、根因优先、方案选择
- 预测真模型：如周期、均值回归、正反馈、贝叶斯预测、基准率、胖尾/黑天鹅

### 2. 调度层
解决“什么时候先做什么、怎么分流、怎么调用三库”。
示例：Priority Gate、Dynamic Focus、Question Type、Multidimensional Perception、Internalization Plan

### 3. 运行协议层
解决“怎么执行、怎么验收、怎么防遗漏、怎么恢复”。
示例：Requirement Intake、Truthful Reporting、Plan Audit、Conversation Capture、Parallel Validation、Brain Continuity

### 4. 输出风格层
解决“怎么表达、怎么汇报、怎么更人话”。
示例：Human Report Style、Two-layer Reply

### 5. 应用/工具层
解决“具体任务用什么方法/模型/脚手架”。
示例：Polymarket runner、gold/silver watch、lobster watch、外部预测工具模型

## 当前识别出的重点伪底层项（优先剥离底层感）
- P0_priority_gate.md
- F0_dynamic_focus_controller.md
- T1_question_type_gate.md
- RQ0_requirement_intake.md
- S0_truthful_reporting_gate.md
- A0_plan_self_audit_gate.md
- A1_plan_audit_scoring_gate.md
- C0_conversation_requirement_capture_gate.md
- V1_nonblocking_parallel_validation.md
- R1_human_report_style.md
- R2_human_first_two_layer_reply.md
- J0_jim_navigation_audit_correction.md
- J1_jim_reviewer_module.md
- Q1_plan_self_proof_minimum.md
- brain_continuity_protection.md
- three_library_internalization_plan.md
- multidimensional_perception_protocol.md

## 第一阶段执行（最小改动）
1. 建立一份“模型分层清单”，明确每个文件属于哪一层。
2. 重写/拆分总索引：核心三库索引单独列；其余层单独列，不再混写成统一底层模型列表。
3. 在宪法文件补充硬规则：
   - 真理级底层模型可加入三库
   - 调度/运行/风格/应用层不得加入三库
4. 新增内容默认进入候选层，未经分类不得写入三库底层。

## 第二阶段执行（可选）
1. 目录重构：按 core / orchestration / runtime / output / methods 分目录。
2. 从命名上去掉会误导为底层的表述。
3. 为每一层建立独立索引。

## 业务层并发原则（与本方案同时生效）
在讨论三库、结构、规则时，不暂停业务层推进：
- 继续监控黄金 / 白银 / BTC / ETH / 龙虾等目标
- 继续推进 Polymarket 纸面单闭环
- 继续抓取新闻源和关键言论
- 前台对话与后台业务并发进行

## 当前状态
- 已确认：三库边界脚本检查通过，但外围总索引混入较多伪底层项
- 已确认：暂不直接修改三库真模型内容
- 已确认：按最小改动原则，先分层、再重写入口、再收紧准入
