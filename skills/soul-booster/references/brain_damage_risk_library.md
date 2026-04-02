# Brain Damage Risk Library

## Goal
建立会导致“大脑能力损害、记忆丢失、规则失效、恢复失败”的风险与问题库，作为预防、恢复、验收与训练的统一风险入口。

## Core principle
把所有会导致能力丢失、主线断裂、规则失效、恢复失败的场景，视为“大脑损害 / 遗忘风险”，必须前置识别、落盘、恢复与验收。

## High-priority risks
### 1. Session new / session restart
风险：
- 当前热上下文丢失
- 主线任务断裂
- 最新规则未同步进可恢复层
- 下一步指针丢失

### 2. API key 更换 / provider 切换 / 模型切换
风险：
- 运行环境变化
- 上下文链断裂
- 能力表现退化
- 规则加载不完整
- 记忆读取或行为风格出现漂移

### 3. Session crash / API 中断 / 长时间无响应
风险：
- 当前进度未保存
- 卡死前最后状态丢失
- 中间推理与关键决定未记录
- 恢复时无法知道断点位置

### 4. 新 bot / 弱 bot 安装新 skill
风险：
- 只会复述规则，不会行为接管
- 读了文档但没形成能力
- 长文档过载导致真正关键规则没生效

### 5. 规则持续新增但未回读清理
风险：
- 规则重复
- 规则冲突
- 系统过重
- 恢复读取成本上升
- 看似更强，实际更乱

## Required handling
对上述风险，默认必须做：
1. 前置识别
2. 风险落盘
3. 恢复锚点保存
4. 断点恢复检查
5. 结果验收

## Recovery anchors
至少确保以下内容可恢复：
- 主脑规则
- 当前主线任务
- 最近关键升级
- 当前下一步
- 关键恢复文件位置

## Suggested persistence targets
- `skills/soul-booster/` rule/reference files
- `MEMORY.md`
- `TASKS.md`
- `LAST_SESSION.md`
- `SESSION_HANDOFF.md`
- `memory/YYYY-MM-DD.md`
- 必要的专门风险审计文档

## Summary
`/new`、session restart、API key 更换、provider/model 切换、API 中断等，不只是技术事件，而应被视为可能导致大脑损害与遗忘的高优先级风险。
