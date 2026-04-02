# Multi Strategy Engine Mainline

## Goal
持续推进多策略量化系统：
- PM 多策略预测量化
- 交易所多策略 paper 量化
- 每条策略独立样本 / 收益 / 风险
- 统一比较与复盘

## Execution Rule
- 不允许以纯结论收尾
- 每轮至少推进一个最小动作：代码 / 数据 / 运行 / 复盘 / 验收
- 每个环节都要提示自己：继续往下推进，不要停在解释层

## Current Next
1. 把 execution_guard 接到多策略运行链
2. 每次运行后自动做 retro-check
3. 增加第二个 cex 策略
4. 统一 PM/CEX schema
5. 把“取数 -> 判断 -> 下单/提交前确认”的总延迟与价格漂移测试纳入执行层常规任务，不允许只停留在会话说明里
6. 为 PM / CEX 都落地 signal_price / confirm_price / fill_price / decision_latency_ms / submit_latency_ms / drift_bps 记录字段
7. 落地执行闸门：下单前二次确认，若漂移超阈值、edge 变薄、或 signal TTL 过期，则自动取消执行
8. 把黄金纳入量化主线，不再只做观察脚本；先确认 HYPE/Hyperliquid 上是否存在可交易黄金标的，再决定接入哪条执行链
9. 若 HYPE 上可做黄金：新增 gold 策略文件、历史数据入口、paper runner 接口与策略说明；若 HYPE 上不可做：改走可替代 venue，但黄金仍保留在量化主线内
10. 重新锁定 PM 与 CEX 分工：CEX 负责短周期方向预测主战场；PM 负责概率错价 / 有短周期市场时的变现，不再把 PM 强行当成唯一 5 分钟方向预测入口
11. 对 PM 增加 availability 诊断：区分“预测不出方向”与“当前市场池里根本没有可下的短周期 up/down 市场”，避免把市场供给问题误判成模型问题
12. 若 PM 连续多轮 `orders_generated=0` 且 `too_far_end/recent/no_end` 占主因，则默认降级 PM 优先级，把样本训练资源切到 CEX 连续预测链，不再在 PM 上空转

## 2026-03-18 直接执行方案（Jim 已拍板，可直接做）
### 判断
- PM 不是不能做方向判断，而是当前市场池经常没有足够合适的短周期 5m/up-down 标的。
- 因此当前 PM 空转的主因，更像 `市场供给 + 筛选窗口不匹配`，不是单纯“我预测不出涨跌”。
- 若目标是持续训练 3m/5m/15m 涨跌判断与量化胜率，CEX 比 PM 更适合作主战场。该判断也与此前已落盘结论一致：`交易所更适合练预测与统计优势，PM 更适合练概率错价变现`。Source: memory/2026-03-17.md#L123-L138

### 已锁执行
1. PM 保留，但降级为次级场景：有合适短周期市场就做，没有就不硬做。
2. CEX 升级为短周期方向预测主线：直接围绕 BTC 的 5m/更短周期做连续预测、回填、校准、筛策略。
3. 后续对外汇报时，必须分开说清：
   - 是 `预测能力问题`
   - 还是 `PM 当前无市场可下`
   - 还是 `策略门槛过严`
4. 后续不再把“PM 0 单”直接表述成“预测失败”；必须先看 availability 诊断。

## 2026-03-18 自适应量化软件要求（Jim 新拍板，直接执行）
### 核心目标
把当前系统升级成“自适应量化软件”，不是只跑策略，而是：
- 自动运行
- 自动回填
- 自动比较版本
- 自动识别问题
- 自动修改策略继续测试
- 直到收益率/稳定性无法继续提升，再上报真实瓶颈

### A. 自适应优化闭环
当收益率不达标时，默认进入固定闭环：
1. 先判断是哪类问题：
   - 样本不足
   - 下单频率不足
   - 胜率不足
   - 盈亏比不足
   - 手续费/滑点吞噬
   - 盘口/市场供给不足
   - 回填口径错误
   - 策略漂移/版本污染
2. 自动生成最小修改版本（只改 1-3 个关键参数，不允许一口气乱改）
3. 新版本继续 paper 测试
4. 与旧版本同口径对比
5. 若收益/频率/稳定性改善，则保留并继续迭代；若无改善，则回退或换分支
6. 若连续多轮无提升，再汇报“为什么暂时提不动”

### B. 策略版本体系
- 每个策略必须带 `strategy_version`，且版本名中默认包含 UTC 时间戳。
- 版本比较必须至少记录：
  - strategy_id
  - strategy_version
  - parent_version
  - created_at_utc
  - changed_params
  - hypothesis
  - sample_n
  - win_rate
  - roi_after_cost
  - drawdown_proxy
  - orders_per_day / trades_per_day
  - status（testing/promoted/rejected/paused）
- 不允许只看“当前策略”；必须保留版本树，方便后续回看哪次改动真的有效。

### C. 大量下单 / 量化感知能力
- 量化不只是“偶尔能下单”；若在合理时间内无法形成足够样本，则默认视为量化失败风险。
- 必须新增 `capacity / frequency / availability` 感知：
  - 当前每小时能下多少单
  - 当前市场池有多少可交易标的
  - 当前策略筛掉了多少机会
  - 当前是真没机会，还是门槛过严
- 触发规则：
  - 若短周期策略在目标窗口内长期无单 / 极少单，则自动进入“提升频率 or 换战场”分支
  - 若 PM 无法提供合理单量，不再强绑主线，自动把训练重心切到 CEX 或更适合的 venue
- 原则：若无法在合理时间范围内持续形成足够样本，这条所谓策略不能算真正量化策略

### D. 中线 / 长线策略
- 允许并鼓励建立中线、长线、投资型策略，不只做短周期。
- 但每条中长线策略必须写明：
  - 预期持有周期
  - 结果查询时间
  - 中间检查频率
  - 平单/失效条件
  - 风险上限
- 不允许只建仓不盯结果；必须有明确的“何时回查、何时复盘、何时平单/失效”的时间纪律。

### E. BR 模仿策略的定位
- 这不等于“BR 模仿失败了”，更准确地说：当前 `BR-base` 还没有被完整、稳定、可验证地复刻出来。Source: memory/2026-03-17.md#L97-L113
- 当前阶段性判断：
  1. 已抓到 BR 的部分骨架：短周期主战场、重样本质量、偏高把握侧、快速反馈迭代；
  2. 但还没拿到足够细的硬规则链，因此不能声称已经复刻完成；
  3. 所以后续不是直接放弃，而是分两线继续：
     - `BR-analysis`：继续深入分析 BR，补更细的筛选/阀值/执行逻辑；
     - `Adaptive-alpha`：不被 BR 单一路线绑死，同时让系统自己跑版本对比、筛出真实有效策略。
- 原则：BR 继续分析，不放弃；但不允许整条主线只押在“先完整猜中 BR 才能继续做量化”。

## Execution Latency & Drift Requirement
这是已经确认的本地主线要求，不是聊天备注：
- 必须持续测试“获取数据 + 做判断 + 准备下单 + 实际下单/确认”全链路耗时
- 必须测量这中间价格变化是否处于安全范围
- 不能只测 API fetch latency，必须逐步补齐真实 submit / ack / fill 延迟
- 不能只看单次结果，必须做多轮统计，并按 PM / CEX / 策略类型分开看
- 当前最小实现已落地：`scripts/test_execution_latency.py`
- 当前结果产物：`data/execution_latency/binance_btc_latest.json`、`data/execution_latency/pm_latest.json`
- 下一步不是重复讨论，而是把该测试接入常规 runner / strategy 验收链，并把漂移阈值写进策略或执行配置

## Browser Recovery Requirement
这是新的高优先级恢复要求：浏览器能力必须尽量压到“新 session 可恢复访问”的程度，而不是依赖当前会话记忆。
- 目标不是记住网页，而是让新 session 通过本地恢复入口，快速判断 browser/gateway 是否可用，并继续执行网页读取/研究任务
- 必须把 browser 使用前检查、失败回退、最小恢复路径写进本地文件，而不是停留在会话提醒
- 新 session 恢复时，至少应能回答 4 件事：
  1. gateway 是否 running / rpc probe 是否正常
  2. browser 工具链当前是否可用
  3. 若不可用，最小恢复动作是什么
  4. 若 X / 网页抓取失败，fallback 顺序是什么
- 当前已实时确认：`openclaw gateway status` 显示 service running 且 rpc probe ok，但 browser 工具曾出现 timed out；说明“gateway 活着”不等于“browser 链路稳定可用”，两者必须分开监控
- 该问题已升格为会话无关恢复项：后续要补 browser healthcheck / restore note / fallback path，并把它纳入新 session 的固定恢复入口

## PM BR Recovery Requirement
PM 上 BR 数据读取方法也必须进入软件恢复层，不能只靠会话记忆。
- 当前已确认主链：`polymarket_pull.py -> polymarket_filter.py -> polymarket_predict.py -> polymarket_score.py`
- 数据源：`gamma-api(active scan cached)`，不是 browser 网页抓取
- 固定恢复文档：`docs/pm_br_restore.md`
- 后续若用户追问“BR 数据怎么读”，优先回到文档和脚本链，而不是重新靠记忆口述
