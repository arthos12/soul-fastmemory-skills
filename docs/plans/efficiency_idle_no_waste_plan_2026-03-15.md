# Plan: efficiency_idle_no_waste (2026-03-15)

## A) 导航
- 主要矛盾：空闲时间被低价值流水线消耗，需求落地（尤其S/A）推进比例过低，导致整体效率低。
- 最值的一刀：把空闲执行机改成“需求落地优先 + 真实落地指标驱动”，并把该能力本身产物化（MVC），让它可以复跑与自查。
- 暂缓/不做：
  - 暂缓新增更多业务需求
  - 暂缓扩预测模型（除非服务落地）

## B) 方案（<=3个候选）
- A: 直接把“空闲不浪费”做成MVC能力（模型卡片+脚本+验收），并把需求状态 pending→mvc（可复用且可验收）
- B: 直接把所有S/A需求都推进到done（大改）
- C: 继续加cron/并发/指标

选择：A（最快、可复用、低风险，且能立刻把“口头效率”变成可跑能力）

## C) 批量修改清单（<=5项）
1) 新增模型卡片：Lx_efficiency_idle_no_waste.md
2) 新增脚本：scripts/efficiency_idle_no_waste.sh（运行需求管线+输出落地报表）
3) 新增验收：docs/mvc_tests/efficiency_idle_no_waste.md
4) 将 triaged 中“效率提升：空闲不浪费”状态从 pending→mvc，并写 artifacts

## D) 验收命令（1条）
```bash
bash scripts/efficiency_idle_no_waste.sh
```

## E) A1 审核（硬否决+评分）
硬否决：PASS（已包含主要矛盾/最值一刀/验收命令/产物清单；不把[m]当[x]）

评分（>=16 PASS）：
- 命中主要矛盾：5
- 速度/成本：5
- 风险：4
- 可验证性：4
总分：18/20 → PASS
