# IDLE_QUEUE.md (Single Source of Truth)

原则：空闲时间只做可验收产出；无产出=失败。

## 当前主线（P0）: 大脑进化最小闭环（判断层）

### Task P0-0: 每个空闲窗口必须新增 1 条“硬纠偏+最小验证”
- Output: `data/brain_evolution/evolution_log.md`
- Done when:
  - 追加 1 条：问题 -> 硬纠偏 -> 最小验证 -> 结果

## P1: Polymarket 预测训练闭环（训练工具，不是主线）

### Task P0-1: 生成预测样本 batch2（≥10条）
- Input: `data/polymarket/markets_sample.jsonl` 或重新拉取 markets
- Output: `data/polymarket/predictions_2026-03-15_batch2.jsonl`
- Run:
  - `python3 scripts/polymarket_pull.py --limit 30 --out data/polymarket/markets_batch2_source.jsonl`
  - （然后由 `scripts/polymarket_predict.py` 生成 batch2）
- Done when:
  - predictions 文件 ≥10 行
  - 每行包含：p_yes_me、p_yes_mkt、modelsUsed、trigger、invalidation

### Task P0-2: 评分并记录一条“最小改动”
- Input: batch2 predictions
- Output:
  - `data/polymarket/score_2026-03-15_batch2.json`
  - `data/polymarket/minimal_change_log.md`（新增 1 条）
- Run:
  - `python3 scripts/polymarket_score.py data/polymarket/predictions_2026-03-15_batch2.jsonl > data/polymarket/score_2026-03-15_batch2.json`
- Done when:
  - score 文件存在
  - minimal_change_log 新增 1 条（只允许 1 条）

## P1: Lobster 监控脚本化
### Task P1-1: API 监控脚本
- Output: `scripts/lobster_watch.sh` + `data/lobster/lobster_ticks.csv`
- Done when:
  - 一条命令可追加一行 tick

## P2: 空闲自检/自修复
- 仅在触发条件出现时执行（网关重启/换模型/失联/连续错误）
- Tool: `scripts/self_check.sh`
