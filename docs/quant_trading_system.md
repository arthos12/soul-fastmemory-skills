# 量化交易系统 - 入口文档

> 本文档整理量化交易核心业务，方便快速恢复上下文

---

## 一、核心定位

**目标**：用程序化方式在 Polymarket 和 CEX 上做量化交易，追求稳定盈利。

**核心理念**：
- 不追求暴利，追求稳定复利
- 区分"卷项目"和"投资"
- 以小博大，注意周期和时效性
- 复利思维，长期主义

---

## 二、当前策略总览

### 2.1 Polymarket 策略

| 策略名 | 定位 | 状态 | 核心参数 |
|--------|------|------|----------|
| pm_br_v2_relaxed | 保活/候选池调试 | paper | minPrice=0.6, maxMinsToEnd=288000 |
| pm_br_v2_highprob | 高概率筛选 | paper | minPrice=0.8, maxMinsToEnd=1440 |
| pm_br_v3_short | 短周期 up/down | paper | minPrice=0.6, maxMinsToEnd=90 |

### 2.2 CEX 策略

| 策略名 | 定位 | 市场 | 状态 |
|--------|------|------|------|
| cex_btc_5m_breakout_v1 | 5分钟 breakout | BTCUSDT 5m | paper (负 ROI) |
| cex_btc_5m_reversion_v1 | 5分钟均值回归 | BTCUSDT 5m | paper (0 trade) |

---

## 三、参考标杆

### 3.1 Top Traders 分析（淘汰低频后）

| Trader | 月度PnL | 交易次数 | 模式 |
|--------|---------|---------|------|
| BoneReader | $453K | 39,313 | 高频量化 |

**关键判断**：交易次数 < 100 的不纳入量化参考。

### 3.2 BoneReader 特征

- 交易次数：39,313
- 历史PnL：$833K
- 增长：20倍
- 最大单笔盈利：$29K
- 模式：高频小额累积

---

## 四、问题分析（持续更新）

### 4.1 BR策略问题分析

**症状：**
| 问题 | 表现 |
|------|------|
| 价格分布偏极值 | 62%仓位在<=0.02 |
| 和BoneReader不像 | 我们低频，BoneReader高频 |
| 假设可能错误 | 把BR当成"低价买入等回归" |

**根因（R0）：**
| 问题 | 根因 |
|------|------|
| 假设错误 | 误解BR本质：BoneReader是"高频套利"，不是"低频等回归" |
| 执行模式错 | 我们低频，BoneReader高频（39,313次） |
| 价格区间错 | 62%在<=0.02，流动性差 |

**前提检查（M3）：**
| 前提 | 是否成立 |
|------|---------|
| BR = 低价买入等回归？ | ❌ 未验证 |
| 低频能做好BR？ | ❌ BoneReader是高频 |
| 0.02以下有足够流动性？ | ❌ 流动性差 |

**结论：**
1. 需要验证BR模式的真正定义
2. 要匹配BoneReader的高频执行模式
3. 价格区间可能需要调整

### 4.2 价格区间策略问题

**当前策略价格分布：**

| 策略 | minPrice | maxPrice | 区间 |
|------|----------|----------|------|
| br_v4_5min_low | 0.001 | 0.01 | 极低 |
| br_v7_reversion | 0.01 | 0.3 | 低价回归 |
| br_v2_brstyle | 0.2 | - | 低价 |
| br_v2_highprob | 0.1 | 0.4 | 低价 |
| br_v5_trend_follow | 0.3 | 0.95 | 宽 |
| br_v6_high_buy_up | 0.5 | 0.95 | 高价追涨 |
| br_v7_trend | 0.5 | 0.95 | 高价追涨 |

**根因分析（R0）：**

| 症状 | 根因 |
|------|------|
| 价格区间乱 | 没有统一逻辑 |
| 覆盖极低到极高 | 什么都想做 |
| 和BoneReader不匹配 | 不知道标杆真正区间 |

**前提检查（M3）：**

| 前提 | 成立？ |
|------|--------|
| 知道BR做什么价格区间？ | ❌ 不知道 |
| 当前区间和标杆一致？ | ❌ 不一致 |
| 有统一筛选逻辑？ | ❌ 没有 |

**结论：** 价格区间策略没有统一逻辑

### 4.3 BoneReader价格区间（关键发现）

**数据源：** data/polymarket/top_traders/br/trades_5000.json (3452条)

| 价格区间 | 数量 | 占比 |
|----------|------|------|
| <0.02 | 101 | 2.9% |
| 其他 | 3351 | 97.1% |

**关键发现：** BoneReader大部分交易在0.4-0.6区间，不是<0.02

**策略改进：** 需要重新分析

### 4.4 我们的持仓数据

**数据源：** data/polymarket/br/positions.json (32条)

| 价格区间 | 数量 | 占比 |
|----------|------|------|
| <=0.02 | 20 | 62.5% |
| 其他 | 12 | 37.5% |

---

## 五、分析框架

### 4.1 核心方法论
```
观察 → 假设 → 验证 → 迭代
   ↑_____________________|
```

### 4.2 分析闭环（5步）

| 步骤 | 动作 | 产出 |
|------|------|------|
| 1. 抓取数据 | 从PM获取Top Traders数据 | raw_data/*.json |
| 2. 提取因子 | 计算价格/时间/类型分布 | factor_*.json |
| 3. 对比差距 | 与我们的策略对比 | gap_analysis.md |
| 4. 产出动作 | 调整策略参数 | new_strategy.json |
| 5. 验证效果 | 回测+实盘验证 | result_*.json |

### 4.3 因子定义（必须量化）

| 因子 | 描述 | 计算方式 |
|------|------|----------|
| **事件类型** | 市场所属类别 | 统计标签分布 |
| **价格分布** | 买入价格区间 | <0.02, 0.02-0.1, 0.1-0.5, >0.5 |
| **持仓时间** | 平均持仓周期 | 5min/15min/1h/1d/+ |
| **资金规模** | 每单金额 | sizeUSD均值 |
| **胜率** | 盈利单比例 | win/total |
| **ROI** | 投资回报率 | profit/size |

---

## 五、数据源

- PM Leaderboard: https://polymarket.com/leaderboard
- 公开Profile: /profile/%40{username}?tab=positions
- Gamma API: https://gamma-api.polymarket.com

---

## 六、每日任务

1. 抓取Top Traders最新数据
2. 提取因子并量化
3. 与我们的策略对比差距
4. 产出可执行动作
5. 记录到迭代日志

---

## 七、后续方向

- 黄金/HYPE 标的纳入
- 多策略组合优化
- 风险控制增强

---

## 八、关键判断标准

### 8.1 量化 vs 非量化
- 交易次数 >= 100 才纳入量化参考
- 低频高盈模式（<100次）不作为量化标杆

### 8.2 策略评估
- 样本量足够才判断有效
- 小样本（<10）不作为策略好坏依据

---

## 九、数据路径（重要）

| 数据 | 路径 | 说明 |
|------|------|------|
| 我们的持仓 | data/polymarket/br/ | 没有top_traders |
| 外部Top Traders | data/polymarket/top_traders/ | 有top_traders |

---

## 十、文件索引

| 文件 | 用途 |
|------|------|
| docs/quant_trading_system.md | 入口文档（本文） |
| docs/current_strategies.md | 策略详细配置 |
| docs/analysis_framework.md | 分析方法论 |
| data/polymarket/top_traders/ | Top Traders原始数据 |
| data/polymarket/reports/ | 分析报告 |
| strategies/ | 策略配置文件 |

---

## 十一、定时任务

### 触发方式
- Heartbeat触发，不是cron

### Heartbeat配置
文件: HEARTBEAT.md

| 任务 | 周期 | 脚本 |
|------|------|------|
| 每小时分析+迭代+检查 | 每小时 | daily_analyzer.py + hourly_work.py |

### daily_analyzer.py 功能
1. 抓取Top Traders数据
2. 分析我们结果
3. 对比差距
4. 记录日志

### hourly_work.py (备用)
每小时检查脚本（非heartbeat）

| 步骤 | 内容 |
|------|------|
| 1. 检查 | 软件运行 + 策略参数 |
| 2. 分析 | 数据分析 |
| 3. 迭代 | 自动调整策略 |
| 4. 验证 | 因子可靠性 |

---

## 十二、核心工具

### 10.1 PM 交易

| 工具 | 用途 |
|------|------|
| pm_paper_loop.py | PM paper 实盘循环 |
| pm_auto_runner.sh | PM 自动运行入口 |
| pm_market_scan.py | PM 市场扫描 |
| pm_dual_side_monitor.py | 双侧监控 |

### 10.2 CEX 交易

| 工具 | 用途 |
|------|------|
| cex_paper_loop.py | CEX paper 实盘 |
| cex_auto_runner.sh | CEX 自动运行入口 |
| binance_trend.py | Binance 趋势监控 |

### 10.3 分析工具

| 工具 | 用途 |
|------|------|
| fetch_top_traders.py | 抓取Top Traders数据 |
| daily_analyzer.py | 每日分析 |
| auto_analyzer.py | 自动分析 |
| br_strategy_backtest.py | BR策略回测 |

### 10.4 监控工具

| 工具 | 用途 |
|------|------|
| monitor_br_pm.py | BR在PM监控 |
| quant_execution_monitor.py | 量化执行监控 |
| check_br_runtime.py | BR运行时检查 |

