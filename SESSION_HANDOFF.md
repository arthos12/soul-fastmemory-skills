# SESSION_HANDOFF.md

## Saved At
- 2026-03-19 17:55 GMT+8

## Current Mainline (Short)
- 量化系统自动运行：PM 四策略 + CEX 两策略自动跑，持续监控与迭代。
- 目标：提高 ROI、稳定性；减少无效订单；提高胜率。
- 系统保护：guard 机制已接入，避免 CPU/内存崩溃。

## Current Status
- PM auto runners：
  - br_v2_highprob (600s)
  - br_v2_brstyle (900s)
  - br_v2_relaxed (900s)
  - br_v3_short (900s)
- CEX auto runners：
  - cex_btc_5m_breakout_v1 (900s)
  - cex_btc_5m_reversion_v1 (900s)
- 近期调整：收紧 PM 过滤（短周期 + edge），并增强 CEX 参数（趋势/量能/回撤阈值）。

## Next Step
1. 按 ROI/胜率/订单数对比策略版本，继续收紧过滤并回退无效改动。
2. 对比 BR 策略与 PM 策略，抽取可迁移模式。
3. 增强停顿原因记录与自动修复（进程/数据断流）。

## Blocker / Constraint
- 不触碰 openclaw/system 文件（避免死机）。
- 策略新增需谨慎、控制模型调用流量。

## Key Files
- scripts/pm_auto_runner.sh
- scripts/cex_auto_runner.sh
- scripts/system_protection_guard.sh
- docs/system_protection_strategy.md
- docs/token_optimization_strategy.md
- strategies/*.json
- data/*/runtime/*_status.json
