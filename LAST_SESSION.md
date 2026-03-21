# LAST_SESSION.md

## Saved At
- 2026-03-21 17:17 UTC

## Active Topic
- PM 量化下单链路：将“扫描→策略过滤→下单”改为一体化高速轮询，重点测试 test 系列 + 尾单策略。

## What’s Done (Recent)
- 修复本地 embedding：Node24 + node-llama-cpp 安装，本地 provider=local 可用（需在 Node24 进程下使用 memory_search）。
- 创建并启用轮跑脚本：`pm_auto_runner_multi.sh`（已停用）。
- 新建一体化扫描下单脚本：`scripts/pm_scan_trade_loop.py`（扫描→过滤→纸单→回填）。
- 轮询间隔改为 30 秒，适配 5m 市场；取消全局去重，多策略可对同一市场下单。
- 日志增强：`data/polymarket/runtime/pm_scan_trade_loop.log` 输出策略/订单/过滤原因。
- 新增扫描原始快照落盘：`data/polymarket/market_snapshot_latest.jsonl`（统计市场出现频次）。
- 使用 openclaw_browser 验证 Polymarket 官网存在 5m 市场，原扫描逻辑过滤过严。

## Current Status
- 运行中：`pm_scan_trade_loop.py`（PID 3792946），策略：br_tail_v1 + test1/test2/test3。
- 主要过滤原因：too_far_end / no_end / no_pick（短周期市场池不足 + 扫描过滤过严）。

## Next Step
1) 检查 `market_snapshot_latest.jsonl` 是否有新增短周期市场。
2) 调整扫描逻辑（提高分页/全量抓取，避免过滤掉 5m/15m）。
3) 若仍无单，收紧/放宽 maxMinsToEnd 并记录版本与结果。

## Constraints
- 2G 服务器，避免高内存/高并发。
- 不触碰 openclaw/system 文件。
