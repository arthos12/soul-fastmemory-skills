# SESSION_HANDOFF.md

## Saved At
- 2026-03-21 17:17 UTC

## Current Mainline (Short)
- PM 量化：已将“扫描→过滤→下单”集成到单一循环脚本，30 秒轮询，重点测试 test 系列 + 尾单。

## Key Changes
- 新脚本：`scripts/pm_scan_trade_loop.py`（扫描+过滤+纸单+回填）。
- 日志：`data/polymarket/runtime/pm_scan_trade_loop.log`（含 orders/results/reasons）。
- 扫描快照落盘：`data/polymarket/market_snapshot_latest.jsonl`。
- 停用旧 runner：`pm_auto_runner_multi.sh`。

## Running Now
- 进程：`pm_scan_trade_loop.py`（PID 3792946）
- 策略：br_tail_v1 + test1_br_copy + test2_follow_br + test3_combined

## Recent Findings
- Polymarket 官网存在 5m 市场；当前扫描逻辑过滤过严导致短周期不足。
- 过滤主要原因：too_far_end / no_end / no_pick。

## Next Step
- 放大扫描范围（分页/全量）并输出 5m/15m 市场清单；持续观察 snapshot 统计。

## Key Files
- scripts/pm_scan_trade_loop.py
- data/polymarket/market_snapshot_latest.jsonl
- data/polymarket/runtime/pm_scan_trade_loop.log
- data/polymarket/reports/hourly_report_*.json
