# Recovery Index

高价值恢复入口总索引。目标：新 session 时先查这里，不靠模糊记忆。

## 1. X / Browser / Twitter 正文读取
### 当前已知事实
- OpenClaw dedicated browser 在当前 root 环境下曾因 sandbox 被拦截，环境约束已查明：root 下需 `browser.noSandbox=true`。
- 历史上曾成功做出并跑通第一版 X 最小阅读器：`scripts/x_browser_reader.js`。
- 该脚本曾成功读取 X 单条正文，且对应 commit 为：`4eaba7a` (`Add minimal X browser reader tool`)。

### 当前恢复状态
- **脚本文件当前不在工作区**（需要优先回查 git / commit `4eaba7a` 恢复）。
- 也就是说：这项能力在记忆中有锚点，但在当前文件层恢复还不完整。

### 恢复动作
1. 先查 git log / `git show 4eaba7a --stat --name-only`
2. 若 commit 存在，从 commit 恢复 `scripts/x_browser_reader.js`
3. 恢复后补一份文档：`docs/x_browser_restore.md`
4. 重新实测单条 X 链接读取

## 2. PM BR 数据读取
### 当前已确认主链
- `scripts/polymarket_pull.py`
- `scripts/polymarket_filter.py`
- `scripts/polymarket_predict.py`
- `scripts/polymarket_score.py`
- `scripts/pm_probability_verify.py`

### 数据源
- `gamma-api(active scan cached)`

### 最新恢复（2026-03-20）
- **BR完整数据文档**：`docs/pm_br_restore.md` ✅
- **BR URL**：`https://polymarket.com/profile/%40BoneReader?tab=positions`
- **浏览器脚本**：`scripts/openclaw_browser.js`, `scripts/openclaw_browser_expand.js`
- **今日数据**：42,891预测，$6,778持仓，$29.2K最大盈利
- 不是 browser 网页抓取

### 恢复文档
- `docs/pm_br_restore.md`

### 最近实测
- 已再次跑通 restore test，pull/filter/predict/score 均成功。

## 3. 使用原则
- 重要复杂能力不能只记在聊天里，必须至少满足：`记忆锚点 + 文件入口 + 可实测恢复`。
- 若用户问“之前那个能力是不是忘了”，先查本索引，再查对应恢复文档与脚本，不准先靠会话印象乱答。
