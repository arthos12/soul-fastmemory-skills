# 量化工作启动清单

## 1. 基础运行 ✅❌

| 检查项 | 命令 | 状态 |
|--------|------|------|
| Runner进程 | `ps aux \| grep pm_auto` | ⬜ |
| 日志输出 | `tail /tmp/br_v4.log` | ⬜ |
| 订单文件 | `ls -la paper_orders_*.jsonl` | ⬜ |

## 2. 策略状态 ✅❌

| 检查项 | 命令 | 状态 |
|--------|------|------|
| 当前策略 | `cat strategies/*.json \| grep name` | ⬜ |
| 参数正确 | minPrice < 0.02 | ⬜ |
| 持仓时间 | maxMinsToEnd < 30 | ⬜ |

## 3. 分析系统 ✅❌

| 检查项 | 命令 | 状态 |
|--------|------|------|
| 定时任务 | `crontab -l \| grep hourly` | ⬜ |
| 分析日志 | `tail ITERATION_LOG.md` | ⬜ |
| 数据更新 | 最近24h有数据 | ⬜ |

## 4. 数据状态 ✅❌

| 检查项 | 命令 | 状态 |
|--------|------|------|
| 订单数 | >0 | ⬜ |
| 已结算 | >0 | ⬜ |
| 待结算 | >0 | ⬜ |

## 5. 数据源一致性（硬规则）✅❌

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 因子数据源真实可用 | 采集=Gamma API | ⬜ |
| 对比/验证来源 | 允许网页抓取 | ⬜ |
| endDate 可用性 | 依赖时间窗口策略必须有 endDate | ⬜ |

## 6. Top Traders ✅❌

| 检查项 | 命令 | 状态 |
|--------|------|------|
| 抓取成功 | yesterday有数据 | ⬜ |
| 分析运行 | 日志有更新 | ⬜ |

## 检查命令

```bash
# 一键检查
python3 scripts/quant_check.py

# 或手动
ps aux | grep pm_auto
ls -la data/polymarket/paper_orders_*.jsonl | tail -3
tail data/polymarket/reports/strategy_analysis/ITERATION_LOG.md
```
