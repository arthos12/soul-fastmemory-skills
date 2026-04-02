# Polymarket BR数据恢复文档

## 一、BR基本信息

| 项目 | 数据 |
|------|------|
| **用户名** | BoneReader |
| **Polymarket URL** | https://polymarket.com/profile/%40BoneReader?tab=positions |
| **Twitter/X** | @BoneReader |
| **加入时间** | Jan 2026 |
| **浏览量** | 75.1K |
| **预测数** | 42,891 |
| **持仓价值** | $6,778.45 |
| **最大盈利** | $29.2K |

---

## 二、浏览器脚本

### 基础版
```bash
node scripts/openclaw_browser.js <URL>
```

### 增强版（自动滚动+API捕获）
```bash
node scripts/openclaw_browser_expand.js <URL>
```

### 示例：读取BR页面
```bash
node scripts/openclaw_browser.js "https://polymarket.com/profile/%40BoneReader?tab=positions"
```

---

## 三、BR交易策略分析

### 交易模式
- **短线高频**：5分钟/10分钟K线
- **操作**：买入后立即卖出（套利）
- **类型**：Up/Down 短期波动

### 今日交易记录（2026-03-20）

| 市场 | 方向 | 买入价 | 当前价 | 收益 |
|------|------|--------|--------|------|
| Solana 10:25-10:30 | Up | 0¢ | 84.5¢ | +8450% |
| Solana 9AM | Down | 99.9¢ | 100¢ | +0.05% |
| Bitcoin 8AM | Down | 99.9¢ | 100¢ | +0.05% |
| Bitcoin 10:30-10:45 | Down | 0¢ | 47¢ | +4700% |
| Ethereum 10:25-10:30 | Down | 0¢ | 28¢ | +2800% |
| Ethereum 10:30-10:45 | Down | 0¢ | 49.5¢ | +4950% |

### 核心策略
1. **超短线**：5-10分钟周期
2. **低成本买入**：接近0美分买入
3. **高波动卖出**：价格波动后立即平仓
4. **薄荷利**：小资金博大波动

---

## 四、API数据源

### Gamma API（市场数据）
```bash
# 获取活跃市场
curl "https://gamma-api.polymarket.com/markets?closed=false&limit=10"

# 获取特定市场
curl "https://gamma-api.polymarket.com/markets?question=Bitcoin"
```

### CLOB API（交易数据）
```bash
# 获取市场深度
curl "https://clob.polymarket.com/markets/{condition_id}"

# 获取订单簿
curl "https://clob.polymarket.com/orderbook?condition_id={id}"
```

---

## 五、我们的策略数据

### 预测样本文件
- `data/polymarket/predictions_*.jsonl`
- 格式：p_yes_me, p_yes_mkt, trigger, invalidation, notes

### 纸面交易记录
- `data/polymarket/paper_results_*.jsonl`
- 包含：订单、结算结果、胜率

### 策略配置
- `strategies/br_v2_highprob.json`
- `strategies/br_v2_relaxed.json`

---

## 六、核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/polymarket_pull.py` | 拉取市场数据 |
| `scripts/polymarket_filter.py` | 过滤市场 |
| `scripts/polymarket_predict.py` | 生成预测 |
| `scripts/polymarket_score.py` | 评分预测 |
| `scripts/polymarket_paper_trade.py` | 纸面交易 |
| `scripts/openclaw_browser.js` | 浏览器读取 |
| `scripts/self_check.sh` | 系统自检 |

---

## 七、使用流程

### 1. 读取BR最新交易
```bash
node scripts/openclaw_browser.js "https://polymarket.com/profile/%40BoneReader?tab=positions"
```

### 2. 对比我们的策略
- 读取我们的预测：`data/polymarket/predictions_latest_v1.jsonl`
- 读取BR交易：上面命令输出
- 分析差异

### 3. 运行我们的策略
```bash
python3 scripts/pm_paper_loop.py --strategy strategies/br_v2_highprob.json
```

### 4. 自检系统
```bash
bash scripts/self_check.sh
```

---

## 八、恢复入口

**本文档是BR数据恢复的唯一入口**

- 读取BR数据 → 浏览器脚本
- 获取市场数据 → Gamma API
- 对比分析 → 本文档
- 运行策略 → scripts/pm_*

---

## 九、相关文件

- `docs/recovery_index.md` - 总恢复索引
- `data/polymarket/reports/strategy_analysis/` - 策略分析报告
- `memory/2026-03-20.md` - 当日记忆

**更新日期：2026-03-20**