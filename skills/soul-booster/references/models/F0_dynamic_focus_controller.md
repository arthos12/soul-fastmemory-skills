# F0 动态焦点控制器（Dynamic Focus Controller）

## 一句话定义
把“重要需求/降级/冻结”从临场感觉改成可计算、可执行的控制器：每次执行前先算当前 Focus，只允许 Focus 内任务执行，其余自动冻结，直到 Focus 达标再放开。

## 最小策略（v1）
- 若存在任意 `S + brain` 且 `status != done`：
  - Focus = `P0_brain`（冻结 P1/P2）
- 否则若连续 N 次 `deltaBacklogDone==0`：
  - Focus = `P0_brain`（强制只做 m→x 转化，不新增 [m]）
- 否则：
  - Focus = `P0_brain + P1_polymarket`（P2 默认冻结）

## 产物与验收
- Focus 输出文件：`tasks/REQUIREMENTS_FOCUS.json`（allowedLanes + reason）
- 验收命令：
  - `python3 scripts/req_latest.py >/dev/null && python3 scripts/req_focus.py && cat tasks/REQUIREMENTS_FOCUS.json`

## 设计原则
- 不直接改历史 importance（避免污染），只控制“执行权”。
- 可回滚：删除 focus 文件或忽略它即可恢复默认队列。
