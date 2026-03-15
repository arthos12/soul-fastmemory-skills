# EFF0 效率底层库（Efficiency Core Library）

## 目标
提供一个统一、可复用的“效率”底层定义与计算框架，用于：
- 解释某个事件里为什么效率低/高
- 指导如何提高效率
- 区分“自我进化效率” vs “需求交付效率”

---

## 一、最底层基础函数（通用）

### 基础函数
**Efficiency = Direction × Utilization × Throughput**

- **Direction（方向正确率，0~1）**：做的事是否命中主线/目标；若跑偏，Direction 直接趋近 0。
- **Utilization（时间利用率，0~1）**：真实执行时间 / 可用时间；空转、秒退会让 Utilization 变低。
- **Throughput（产出速率，>=0）**：单位时间有效产出。

> 解释：
> - 只提速但跑偏（Direction≈0）= 伪效率
> - 一直在跑但空转（Utilization≈0）= 假忙
> - 方向对且不空转，但产出慢（Throughput低）= 执行力/方法问题

### 快速诊断（先判哪一项坏）
- done 不涨 + 做了一堆事 → 先查 Direction
- cron 一直跑但几乎没产物 → 先查 Utilization
- 方向对也在干活，但推进慢/返工多 → 先查 Throughput

---

## 二、需求交付效率（delivery）

### 定义
**E_delivery = Direction_delivery × Utilization_runtime × DoneRate**

- **DoneRate**：`Δdone / Δt`
- **完成度快照（占比）**：`done / (done + mvc)`（用于状态，不等于速率）
- **Utilization_runtime**：`active_exec_time / wall_time`（避免空转）
- **Direction_delivery**：执行是否集中在 S/A 且 m→x（否则降权）

### 对用户汇报必答四项（人话优先）
1) 并发（WIP/同时跑几条 lane）
2) 时间利用率（有多少时间在真干活）
3) 空转多久（没产出的时间）
4) 最终完成数量与占比（done 增量 + done/(done+mvc)）

---

## 三、自我进化效率（brain）

### 定义
**E_brain = Direction_brain × Utilization_brain × ErrorDropRate**

- **ErrorDropRate**：同类错误复发率下降速度（例如跑偏/纠错慢/漏抓重点）
- **Direction_brain**：改动是否直接增强“判断/纠错/不复发”，而不是堆文档
- **Utilization_brain**：改动是否形成可执行闸门+验收（否则视为空转）

### 对用户汇报（人话）
- “同类错误是否在接下来 N 次对话里减少/归零？”
- “纠错是否能做到 1 轮内改对？”
- “是否有防复发闸门落盘？”

---

## 四、事件应对：如何用本库解释与提高效率

### 事件模板（固定三段）
1) **先定效率范围**：这次是 delivery 还是 brain（或两者）？
2) **定位短板项**：Direction / Utilization / Throughput 哪个最差？
3) **给最值一刀**：只改最差项的一刀，并给验收。

---

## 五、硬规则（防伪效率）
- 任何“提效”必须说明：改善的是 Direction / Utilization / Throughput 哪一项。
- **提效顺序固定**：先 Direction（方向正确）→ 再 Utilization（时间利用率，避免空转）→ 最后 Throughput（产出速率/并发）。
  - 方向错 = 乘以 0；并发/利用率不能替代方向正确。
- 任何“完成”必须以 `[x]/done` 与可复跑证据为准。
- 若 Direction 低：先修聚焦/闸门；若 Utilization 低：再修执行器/空转；若 Throughput 低：最后才谈并发与流程优化。
