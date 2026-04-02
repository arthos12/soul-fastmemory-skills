# SESSION_RECOVERY.md

目的：给 **新 session 的我自己** 看，不是给 Jim 看。

如果 session 被 `/new`、压缩、中断、重启，不要靠模糊记忆。先读这里，再继续做事。

---

## 1. 当前主线
当前主线不是闲聊，也不是单点脚本，而是：
- 持续推进多策略量化系统
- PM + CEX 并行
- 把策略、执行、恢复、验证都压到本地文件/脚本层
- 降低对会话记忆的依赖

主任务文件：
- `tasks/multi_strategy_engine.md`

---

## 2. 当前关键恢复入口
### 策略说明（先看这个，再看 JSON）
- `docs/current_strategies.md`

### PM BR 数据恢复
- `docs/pm_br_restore.md`

### 外部文章/策略线索备份
- `docs/pm_strategy_article_notes.md`

### 总恢复索引
- `docs/recovery_index.md`

---

## 3. X / 浏览器读取能力
### 当前事实
- 当前能直接用：`scripts/openclaw_browser.js`
- 它可以读取单条 X 页面正文
- 旧名线索：`scripts/x_browser_reader.js`
- 相关 commit：
  - `4eaba7a` Add minimal X browser reader tool
  - `06014e5` Rename X browser reader to openclaw browser

### 重要区别
- “当前能用脚本读 X” = true
- “OpenClaw dedicated browser 工具链历史上完全稳定” ≠ 已确认
- 所以以后不要把这两件事混成一件事

---

## 4. PM BR 数据恢复结论
- BR 数据主链不是靠 browser 网页抓取
- 主链是：
  - `scripts/polymarket_pull.py`
  - `scripts/polymarket_filter.py`
  - `scripts/polymarket_predict.py`
  - `scripts/polymarket_score.py`
  - `scripts/pm_probability_verify.py`
- 数据源：`gamma-api(active scan cached)`

---

## 5. 新 session 的默认动作
如果 Jim 提到：
- 浏览器脚本
- X 读取
- BR 数据
- 当前在跑的策略
- 之前读过的策略文章

不要靠印象回答，默认先回查：
1. `SESSION_RECOVERY.md`
2. `docs/recovery_index.md`
3. 对应专项文档
4. 必要时直接实测

---

## 6. 新默认规则
- 重要能力不能只存在会话里
- 新策略/新恢复入口/新外部策略线索，默认同时写：
  - 文档入口
  - 任务/恢复入口
  - 必要记忆锚点
- 以后若 Jim 又需要亲自翻聊天记录帮我找，视为恢复链失败，不算完成
