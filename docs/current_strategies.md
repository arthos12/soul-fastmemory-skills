# Current Strategies

目的：把当前正在执行/测试的策略，用人能快速看懂的文字写清楚，方便后续 session 直接恢复理解，不必先读代码或猜配置。

---

## 总览
当前 registry 中启用的策略共 5 条：
- PM paper: 3 条
- CEX paper: 2 条

策略索引来源：`strategies/strategy_registry.json`

---

## 1. pm_br_v2_relaxed
- 类型：PM paper
- 配置文件：`strategies/br_v2_relaxed.json`
- 当前定位：**宽松版 PM 高概率筛选策略 / 保活与候选池调试策略**

### 规则摘要
- `mode = highprob`
- `minPrice = 0.6`
- `maxMinsToEnd = 288000`
- `maxOrders = 40`
- `sizeUSD = 50`
- `source = gamma-api(active scan cached)`

### 人话说明
这条不是严格 BR 主基线，而是一个更宽松的 PM 候选池策略。目的是：
- 先保证 paper 链路能持续出样本
- 给回填、报告、复盘、验证链提供持续数据
- 帮助发现候选池、去重、筛选、报告链中的问题

### 注意
- 它更偏 `debug/保活池`，不是最终严谨策略。
- 不能把它的出单结果直接当成真实量化能力完成。

---

## 2. pm_br_v2_highprob
- 类型：PM paper
- 配置文件：`strategies/br_v2_highprob.json`
- 当前定位：**更接近 BR 骨架的高概率筛选策略**

### 规则摘要
- `mode = highprob`
- `minPrice = 0.8`
- `maxMinsToEnd = 1440`
- `maxOrders = 40`
- `sizeUSD = 50`
- 关键词：`bitcoin/btc/ethereum/eth/solana/sol/xrp/up or down`
- `source = gamma-api(active scan cached)`

### 人话说明
这条比 relaxed 更严格：
- 只看更高概率侧
- 时间窗口更近
- 市场范围更聚焦在 crypto / up-or-down 场景

### 用途
- 用来逼近“更像 BR 的高把握市场选择”
- 适合做与 relaxed 的对照

### 注意
- 仍然属于 paper / 验证阶段
- 不是已证实有效的成熟真钱策略

---

## 3. pm_br_v3_short
- 类型：PM paper
- 配置文件：`strategies/br_v3_short.json`
- 当前定位：**短周期 up/down 版本，偏向更贴近短时执行机会**

### 规则摘要
- `mode = highprob`
- `minPrice = 0.6`
- `maxMinsToEnd = 90`
- `maxOrders = 30`
- `sizeUSD = 50`
- 关键词：`up or down` + 主流币关键词
- `source = gamma-api(active scan cached)`

### 人话说明
这条是更短周期的 PM 策略：
- 优先找快到期的 up/down 市场
- 更接近短时判断 / 短时执行的研究方向

### 用途
- 用来研究短周期市场是否更适合高频验证
- 也更接近“Binance -> PM 延迟/反应”这类机会的潜在落点

### 注意
- 样本可能更少、更跳、噪声更大
- 需要更严谨的延迟/漂移/盘口检查

---

## 4. cex_btc_5m_breakout_v1
- 类型：CEX paper
- 配置文件：`strategies/cex_btc_5m_breakout_v1.json`
- 市场：`BTCUSDT @ Binance 5m`
- 当前定位：**5 分钟 breakout 测试策略**

### 规则摘要
- `holdBars = 1`
- `feeBps = 10`
- `slippageBps = 5`

### 人话说明
这条策略假设：
- BTC 5 分钟级别如果出现 breakout，可能延续至少一个 bar
- 因此入场后只持有 1 根 bar 做最小验证

### 当前已知情况
- 它已经产生过真实 paper 样本
- 扣掉手续费/滑点后，当前版本结果偏负

### 用途
- 用来快速筛掉“看起来合理但实际不赚钱”的策略
- 给多策略系统提供一个可比较的 CEX 基线

---

## 5. cex_btc_5m_reversion_v1
- 类型：CEX paper
- 配置文件：`strategies/cex_btc_5m_reversion_v1.json`
- 市场：`BTCUSDT @ Binance 5m`
- 当前定位：**5 分钟均值回归测试策略**

### 规则摘要
- `holdBars = 1`
- `feeBps = 10`
- `slippageBps = 5`
- `mode = reversion`

### 人话说明
这条策略假设：
- 某些 5 分钟偏离会回归
- 因此尝试做反向、短持有的 paper 测试

### 当前已知情况
- 目前 0 trade，说明在现有条件下尚未触发
- 当前没有足够样本来判断它好坏

---

## 当前阅读原则
1. `pm_br_v2_relaxed` 更偏保活/调试池，不要拿它冒充最终策略。
2. `pm_br_v2_highprob` / `pm_br_v3_short` 更接近真正需要验证的 PM 策略方向。
3. CEX 两条是用来建立多策略比较框架，不是已经跑出来的真钱系统。
4. 看策略时，不只看名字和参数，还要看：
   - 它的定位是什么
   - 它是 debug 还是正式验证
   - 它当前是否已有样本
   - 结果是否已扣费/滑点

## 黄金 / HYPE 新方向（已纳入主线）
- Jim 已明确要求：把黄金也纳入量化，并检查 HYPE/Hyperliquid 上能不能做。
- 当前本地已存在黄金观察入口：`scripts/gold_silver_watch.py` / `scripts/gold_silver_watch.sh`。
- 但当前真实状态仍只是“观察脚本已存在”，还没有进入多策略量化执行层。
- 当前最小正确推进顺序：
  1. 先确认 HYPE/Hyperliquid 上是否存在可交易黄金相关标的；
  2. 若存在，补 gold 策略、数据入口、paper 验证与说明文档；
  3. 若不存在，换 venue，但黄金仍保留在量化主线里，不因 venue 不合适而丢弃。

## 后续要求
- 新增或修改策略时，默认同步更新本文件。
- 不允许只改 JSON 不写说明，否则新 session 很容易只看到参数，看不懂意图。
