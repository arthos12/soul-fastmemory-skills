# HEARTBEAT.md - 定时任务

## 触发规则
- 每小时 GMT 08:00, 09:00, 10:00... (每小时一次)

## 任务内容

### 1. 检查 (hourly_work.py)
检查量化软件是否运行 + 检查策略参数是否正确
- Runner进程状态
- 策略参数（minPrice, maxMinsToEnd）

### 2. 分析 + 迭代 (daily_analyzer.py)
分析我们数据结果 + 发现问题就自动改策略
- 统计单数、已结算数
- 价格分布（低价<0.1, 高价>0.7）
- 对比BR差距
- 自动调整策略参数

### 3. BR分析 (daily_top_trader_analysis.sh)
抓取Top Traders数据 + 对比因子 + 调整策略
- 抓取BR最新数据
- 分析因子差异
- 记录迭代日志

### 4. 自动分析 (auto_analyzer.py)
加载我们结果 + 价格分布统计 + 和BR对比
- 统计价格分布
- 和BR对比
