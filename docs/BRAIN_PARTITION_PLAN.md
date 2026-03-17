# 大脑分区方案 v1（底层三库 + 自我进化脑）

目标：降低“规则/项目/复盘/迭代”混在一起导致的漂移；让复盘能稳定产出“根因→修复→再跑”的闭环。

## 分区结构（最小可行）

### 1) CORE（底层硬规则库）
- 放什么：必须长期稳定、跨项目通用、能强约束行为的规则
- 文件：
  - `SELF_OPERATIONS.md`（执行闭环、检查节奏、复盘范围与要求）
  - `MEMORY.md`（长期硬规则与偏好，不写流水账）

### 2) PROJECT（项目执行库）
- 放什么：每个项目的目标、当前状态、策略参数、数据口径、验收标准
- 文件示例：
  - `tasks/BR_YINFU_STRATEGY_CARD.md`
  - `strategies/*.json`
  - `tasks/OPS_PRIORITY_PM_SECONDARY.md`

### 3) EVIDENCE（证据与数据产物库）
- 放什么：可复查的订单、回填、报告、脚本输出
- 文件示例：
  - `data/polymarket/paper_orders_*.jsonl`
  - `data/polymarket/paper_results_*.jsonl`
  - `data/polymarket/reports/hourly_report_*.json`

---

## 自我进化脑（EVOLVE）

### 4) EVOLVE（自我进化与复盘修复库）
- 放什么：复盘日志 + 根因库 + 修复补丁记录 + 复盘后的改动链接
- 目录：`docs/retrospectives/`（每小时/每8小时）
- 核心规则：复盘必须输出“根因分类 + 修复动作 + 已执行证据 + 下一轮验收”。

### 根因分类（建议固定）
- D: Data（数据源/口径/缓存/过滤）
- S: Strategy（策略假设/阈值/过滤/市场选择）
- E: Execution（执行节奏/回填/监控/并发）
- V: Verification（验收/统计/回测/ROI审计）
- R: Rule/System（底层规则漂移/变更闸门失效）

---

## 运行方式（把复盘变成“改完就跑”）
- 每次复盘输出三件事：
  1) **Top3 根因**（按影响目标排序，带分类 D/S/E/V/R）
  2) **每个根因 1 个最短修复动作**（可在30分钟内完成）
  3) **已执行证据**（commit id / 新文件 / 新报告）
- 复盘后立即进入下一轮运行（不能停在复盘文本上）。
