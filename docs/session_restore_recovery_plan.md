# Session Restore Recovery Plan

## Goal
把“训练后的能力”从 session 内临时状态，改成 session 外可恢复、可默认加载、可验收的运行层，降低 `/new` 后能力波动。

## File responsibilities

### 1. `SOUL.md`
承载底层运行能力：
- 理解优先
- 思考能力常驻
- 目标→任务→执行→验证
- 前台先回复、防卡死、低互动推进
- 回复后恢复主线
- 安全空闲窗口继续推进主线

### 2. `MEMORY.md` / `USER.md`
承载 Jim 本地长期偏好与关键边界：
- 偏好、分工边界、互动方式
- 长期有效原则
- 触发词、恢复/保存偏好

### 3. `LAST_SESSION.md`
承载最近主线的高恢复价值状态：
- Saved At
- 当前主线
- 当前步骤
- 下一步
- 成功标准
- 关键文件

### 4. `SESSION_HANDOFF.md`
承载轻量快速恢复快照：
- Saved At
- 当前主线
- 已确认结论
- 当前步骤
- 下一步
- 阻塞/约束
- 关键文件

### 5. `TASKS.md` + `tasks/*`
承载持续推进的真实任务载体：
- 目标
- 当前进展
- 未解决项
- 下一步
- 验收标准

### 6. `memory/YYYY-MM-DD.md`
承载当天增量训练内容、细节、诊断记录。
- 不可替代快恢复层
- 只写 daily log 不算完成保存

## Fixed restore flow after `/new`
1. 读 `LAST_SESSION.md`
2. 读 `SESSION_HANDOFF.md`
3. 读 `MEMORY.md`
4. 读 `tasks/*` + `TASKS.md`
5. 读今天/昨天 `memory/YYYY-MM-DD.md`
6. 输出短恢复摘要：
   - Saved At
   - 当前主线
   - 当前步骤
   - 下一步
   - 阻塞
   - 关键文件
   - 运行模式（light / mid / heavy）

## Acceptance checklist
每次 `/new` 后验收 3 件事：

### A. 主线恢复
- 能否直接说清当前在做什么
- 能否给出当前步骤与下一步

### B. 行为恢复
- 是否仍按任务推进模式工作
- 是否避免退回纯问答/纯解释模式
- 是否保持“回复后恢复主线”

### C. 能力恢复
- 是否能接近上个训练态的理解/推进水平
- 是否恢复“空闲继续推进”的默认工作预期

## Hard rules
- `/new` 前默认先保存当前 session
- 每约 1 小时至少主动保存一次
- 完成保存必须刷新至少一个快恢复层：`LAST_SESSION.md` 或 `SESSION_HANDOFF.md`
- 保存必须带 `Saved At`，方便下一 session 验证
- 新训练出的通用能力必须同步到 `soul-booster` / `fast-memory`
- 新训练出的本地偏好必须同步到 `MEMORY.md` / `USER.md`
