# root_cause_log.md

用于记录“症状→共因根因→最小修复→指标验收”。

## 2026-03-15
- 症状：效率提升推理跑偏；动作多但对目标贡献小；空闲吞吐假高。
- 根因层级：目标函数/指标缺失（目标未量化，无法剪枝）。
- 共因：没有把提效动作绑定到可量化指标与验收闸门，导致做事无法比较收益。
- 最小共因修复：引入 E0 效率闸门 + metrics.jsonl（并在 idle_dispatcher 写入 recentFiles2m 等产出代理）。
- 验收：`tail -n 3 data/efficiency/metrics.jsonl` 看到 recentFiles2m 与吞吐指标持续记录。
