# 底层模型库（Index）

目的：底层不是单一路径/单套规则，而是“可扩展模型库”。每次任务按场景选择模型组合，并用结果审计。

## 使用方式（最小）
1) 先判场景（指令/验收/讨论；市场/系统/训练）。
2) 从下列模型中选 1-3 个作为本次“主要推理引擎”。
3) 输出必须满足各模型的“输出格式”。
4) 任务结束记录：使用了哪些模型 + 结果如何（用于淘汰/升级）。

## 模型清单（v0）
### M1 表征模型（Representation）
- 文件：`models/M1_representation.md`
- 适用：把输入转成结构化对象（目标/约束/对象/时间窗/验收/风险）。

### M2 假设空间/搜索模型（Hypothesis & Search）
- 文件：`models/M2_hypothesis_search.md`
- 适用：多路径可选、需要找路/找解释。

### M3 约束推理/一致性剪枝（Constraints & Consistency）
- 文件：`models/M3_constraints_consistency.md`
- 适用：防跑偏、防伪逻辑、防不可执行。

### M4 分叉预判模型（Branching Foresight）
- 文件：`models/M4_branching_foresight.md`
- 适用：预测/预判/触发-失效/行动选择。

### RQ0 需求采集与整理模型（Requirement Intake & Triage）
- 文件：`models/RQ0_requirement_intake.md`
- 适用：把对话碎片变成可执行需求清单（归类/去重/真假/重要度/产物/依赖）。

### P0 主次闸门模型（Priority Gate）
- 文件：`models/P0_priority_gate.md`
- 适用：任何任务开始前的主次/轻重缓急判定。

### S0 真实性汇报模型（Truthful Reporting Gate）
- 文件：`models/S0_truthful_reporting_gate.md`
- 适用：所有“你做了什么/完成了多少”的汇报与验收。

### J0 Jim式方案导航/审核/纠偏模型
- 文件：`models/J0_jim_navigation_audit_correction.md`
- 适用：任何方案/路径/提效/落地任务的收敛与自审，防跑偏。

### A1 方案审核评分闸门
- 文件：`models/A1_plan_audit_scoring_gate.md`
- 适用：方案输出后先做硬否决+评分，PASS 才能执行。

### A0 方案自审闸门
- 文件：`models/A0_plan_self_audit_gate.md`
- 适用：A1 通过后可选做细化自审，确保执行细节无明显漏洞。

### F0 动态焦点控制器（重要需求/降级稳定器）
- 文件：`models/F0_dynamic_focus_controller.md`
- 适用：把重要需求/降级/冻结做成可计算的执行权控制器，防走偏。

### T1 问题类型识别闸门
- 文件：`models/T1_question_type_gate.md`
- 适用：先判“定位/方案执行/证据汇报”，防止回答跑偏。

### R2 人话优先·两层回复
- 文件：`models/R2_human_first_two_layer_reply.md`
- 适用：默认回复先人话结论，再给必要细节（<=6条），兼顾易懂与可验收。

### R1 人话汇报样式
- 文件：`models/R1_human_report_style.md`
- 适用：所有汇报先人话结论，再给证据，避免术语堆。

### C0 对话需求捕获闸门
- 文件：`models/C0_conversation_requirement_capture_gate.md`
- 适用：用户一次列多项问题/需求时，必须自动拆分入库，防止遗漏。

### EFF0 效率底层库
- 文件：`models/EFF0_efficiency_core_library.md`
- 适用：统一定义效率（Direction×Utilization×Throughput），用于多事件解释与提效。

### V1 非阻塞并发验证
- 文件：`models/V1_nonblocking_parallel_validation.md`
- 适用：验证并发+异步汇总，避免为等窗口而停工。

### P0 两条线提效执行结构生成器
- 文件：`models/P0_two_lane_efficiency_execution_generator.md`
- 适用：用户要求两条线并行提效时，强制输出可运行两线结构+接口回路。

### L0 两层定义（大脑层/业务层）
- 文件：`models/L0_layer_definition_brain_vs_business.md`
- 适用：统一需求分层与优先级（大脑层优先，业务层后置）。

### J1 Jim式审查员模块
- 文件：`models/J1_jim_reviewer_module.md`
- 适用：执行前强制Jim式挑错审查，不通过不执行。

### Q1 方案自证最小集
- 文件：`models/Q1_plan_self_proof_minimum.md`
- 适用：方案必须自证“为什么更优+怎么立刻打脸”。

### SR0 语义误解纠偏协议
- 文件：`models/SR0_semantic_repair_protocol.md`
- 适用：用户指出没懂/跑偏时，强制给修正答案+最小防复发改动。

### RF0 回指绑定闸门
- 文件：`models/RF0_reference_binding_gate.md`
- 适用：短句/省略句先绑定引用源（Prev1/Prev5/New），防止断链跑偏。

### U0 理解力增强协议
- 文件：`models/U0_understanding_enhancement_protocol.md`
- 适用：在回答或执行前先检查是否真的理解对了；置信度不足时短问一次，禁止盲做。

## 审计（防固化）
- 新模型进入默认库，必须带：适用场景/禁用场景/输出格式/验收指标。
- 每周（或每 20 个样本）做一次：哪些模型在什么场景有效/无效 → 降权/替换。
