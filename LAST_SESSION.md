# LAST_SESSION.md

## Saved At
- 2026-03-19 17:55 GMT+8

## Active Topic
- 自动化量化运行 + 策略迭代（PM/BR/CEX），以 ROI/胜率/稳定性为主指标。

## What’s Done (Recent)
- 启动 PM 4 策略自动跑 + CEX 2 策略自动跑。
- 上线 system protection guard（CPU/内存阈值保护）。
- 收紧 PM 短周期/edge 过滤；调整 CEX 参数（趋势/量能/回撤阈值）。
- 增加跨平台价差监测脚本（arb_spread_check.py）。

## Next Step
- 继续用“订单数→胜率→ROI”闭环对比版本，保留有效改动。
- 持续对比 BR 数据模式与 PM 策略。
- 补充停顿原因记录与自动修复链路。

## Constraints
- 不触碰 openclaw/system 文件。
- 规则落盘避免膨胀与不协调。
- 策略新增谨慎，流量可控。
