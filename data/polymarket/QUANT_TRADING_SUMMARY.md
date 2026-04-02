# Polymarket 量化交易完整资料

## 一、系统架构

### 核心组件
| 组件 | 路径 | 功能 |
|------|------|------|
| Runner | scripts/pm_auto_runner.sh | 自动下单循环 |
| 市场扫描 | scripts/market_scanner.py | 每5分钟扫描市场 |
| 策略文件 | strategies/*.json | 交易参数配置 |
| Cron定时 | scripts/hourly_work.py | 每小时分析迭代 |

### 目录结构
```
data/polymarket/
├── top_traders/     # BR等高手数据
│   └── br/          # BoneReader原始数据 (3452单)
├── ours/            # 我们的模拟数据 (32单)
├── reports/         # 分析报告
│   └── strategy_analysis/
├── cache/           # 市场缓存
└── paper_orders_*.jsonl   # 订单记录
```

---

## 二、BR (BoneReader) 分析

### 真实数据
- 总交易: **3452单**
- 月盈利: **$452K**
- 持仓周期: **5-15分钟**

### 价格分布（重要发现！）
| 价格区间 | BR占比 | 我们的占比 |
|----------|--------|------------|
| ≤0.02 | **3.1%** | 18.8% ❌ |
| 0.40-0.60 | **37.5%** | - |
| ≥0.90 | **30.9%** | 46.9% |

**结论：BR主要在 ≥0.40 中高价位买入（81%），不是极低价！**

### 币种分布
- Bitcoin: 38%
- Ethereum: 9%
- Solana: 7%
- XRP: 8%

---

## 三、当前策略参数

| 策略名 | minPrice | maxMinsToEnd | 状态 |
|--------|----------|--------------|------|
| br_v4_5min_low.json | 0.001 | 15 | 当前使用 |
| br_v2_highprob.json | 0.3 | 60 | - |
| br_v3_short.json | 0.001 | 10 | - |

---

##