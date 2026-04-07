# Session Memory（会话记忆）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/SessionMemory/sessionMemory.ts`

## 核心机制

### 功能
在对话过程中自动维护一个 markdown 文件，记录会话的关键信息。
不依赖长期记忆，在会话内自我维护。

### 运行方式
```typescript
// 用 forked subagent 在后台更新
registerPostSamplingHook(async (context) => {
  // 每次采样完成后检查是否需要更新 session memory
  if (hasMetUpdateThreshold(context)) {
    await runForkedAgent(updateSessionMemory)
  }
})
```

### 触发条件
```typescript
hasMetUpdateThreshold(context) → boolean
hasMetInitializationThreshold(context) → boolean

// 更新阈值：
// - 距离上次更新超过 N 条消息
// - 或者距离初始化超过 N 条消息
```

### 存储位置
```
~/.claude/projects/{project}/session memory.md
```

### 会话结束时
```typescript
// 会话结束或中断时
// 自动提取关键信息到长期记忆
// 清理 session memory
```

## Claude Code 的关键设计

### 两阶段生命周期

**阶段1：初始化**
- 当消息数达到初始化阈值时创建 session memory
- 写入会话元信息（开始时间、项目、目标）

**阶段2：增量更新**
- 每次采样完成后检查更新阈值
- 后台 fork agent 执行更新
- 只更新变化的部分

**阶段3：会话结束**
- 提取高价值信息到长期记忆
- 清理 session memory 文件
- 更新索引

### 与长期记忆的关系

```
Session Memory → 长期记忆
     ↓
  会话结束时的整合
     ↓
  记忆沉淀
```

## OpenClaw 版本设计

### 文件结构
```
memory/
  sessions/
    {session_id}/
      session.md      # 会话记忆
      messages.json   # 消息历史（可选）
      meta.json       # 元信息
```

### Session Memory 内容
```markdown
# Session Memory

## 会话目标
[用户在做什么]

## 当前进展
- [已完成步骤]
- [当前步骤]

## 关键信息
- [用户偏好]
- [项目状态]

## 下一步
[待处理事项]
```

### 更新时机
- 每次响应后检查阈值
- 关键决策时立即更新
- 会话结束时强制整合

### 整合流程
```
1. 读取 session memory
2. 识别高价值信息
3. 按类型写入长期记忆（user/feedback/project/reference）
4. 清理 session memory
```

## 与现有 Fast-Memory 的整合

现有系统已有：
- 分层存储（长期/近期/日志/缓冲）
- S/A/B 保存分级
- 四分类（user/feedback/project/reference）

新增：
- 会话级别的自我维护
- 后台增量更新
- 会话结束的自动整合

## 核心原则

1. **不污染长期记忆** — 会话内的细节先存 session
2. **自动维护** — 不需要人工触发
3. **可恢复** — 中断后能继续
4. **会话结束时整合** — 精华沉淀，冗余清理

---
*整合自 Claude Code sessionMemory.ts 模块，2026-04-07*
