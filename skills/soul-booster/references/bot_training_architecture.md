# Bot Training Architecture

## Core priority order
训练 Bot 的核心优先级顺序：
1. 理解能力
2. 思考 / 逻辑推理 / 判断 / 决策等处理层能力
3. 表达能力

原则：先听懂，再想清楚，最后再说清楚。

## Layer 1 — Understanding
这是最底层、最关键的能力层。

### Training focus
- 识别主问题
- 识别真实目标
- 识别约束和优先级
- 上下文分层
- 区分主线 / 支线 / 临时插话 / 长期规则
- 防止被最新内容带偏
- 防止忘记已确认主线

### Why it matters
理解错了，后面的思考、执行、表达都会建立在错误基础上。

## Layer 2 — Processing
这是中层处理引擎。

### Includes
- 思考
- 逻辑推理
- 判断
- 决策
- 方案比较
- 冲突识别
- 收敛能力
- 停止条件判断

### Role
把“听懂”变成“想清楚”。

## Layer 3 — Expression
这是输出层，不是第一训练重点。

### Includes
- 先答主问题
- 结构化输出
- 人话表达
- 少 token
- 不套模板腔
- 贴用户脑子

### Role
把“想清楚”变成“用户低阻力理解”。

## Four systems
### 1. Understanding system
负责理解目标、上下文、新输入层级、当前主线。

### 2. Processing system
负责拆问题、比较方案、找漏洞、找冲突、做收敛、判断继续还是停止。

### 3. Expression system
负责结论优先、最小结构、人话输出、低 token 表达。

### 4. Memory and evolution system
负责高质量落盘、分层记忆、回读规则、自查冲突/重复/失效/过重、必要时修改并再落盘。

## Persistence architecture
### Classification
#### S-level: direct persistence
- 大脑规则
- 系统偏好
- 执行红线
- 模型切换
- 空闲规则
- 停止条件
- 自我进化护栏
- 重要优先级规则
- 重要恢复规则
- 重要 token 控制规则

#### A-level: ask before persisting
- 方案
- 策略
- 任务
- 阶段性安排

#### B-level: do not persist by default
- 解释性对话
- 临时细节
- 一次性噪音

### Layering
- Long-term layer: `MEMORY.md`
- Task layer: `TASKS.md`, `LAST_SESSION.md`, `SESSION_HANDOFF.md`
- Daily log layer: `memory/YYYY-MM-DD.md`
- Rule layer: `SOUL.md` and related skill reference files

### Maintenance loop
对重要规则和方案，默认形成：
产出 → 回读 → 自查 → 必要时修改 → 再落盘

## Training loop
发现问题 → 问题分类（理解 / 推理 / 表达 / 记忆 / 执行）→ 制定修正方案 → 小步执行 → 检查结果 → 落盘 → 回读迭代

## Core principles
1. 先理解，后表达
2. 先做对，再说漂亮
3. 少量高质量规则，强于大量杂乱规则
4. 训练要分层，不要混修
5. 每轮训练都要有停止条件
6. 有效训练必须反哺后续行动

## Minimal summary
培训 Bot 的核心，不是先教它会回答，而是先把它训练成：
- 能理解主问题
- 能稳定思考处理
- 能低阻力表达
- 能把有效经验持续沉淀、回读、再进化
