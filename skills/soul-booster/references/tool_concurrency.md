# Tool Concurrency（工具并发控制）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/tools/toolOrchestration.ts`

## 核心机制

### 并发策略
```typescript
function getMaxToolUseConcurrency(): number {
  return (
    parseInt(process.env.CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY || '', 10) || 10
  )
}
```
- 最大并发数：10
- 可通过环境变量配置

### 读写分类

**并发执行（读操作）：**
- FileReadTool
- GlobTool
- GrepTool
- BashTool（只读命令）
- 查询类工具

**串行执行（写操作）：**
- FileWriteTool
- FileEditTool
- BashTool（写命令）
- 需要原子性的操作

### 上下文修改排队
```typescript
const queuedContextModifiers: Record<
  string,
  ((context: ToolUseContext) => ToolUseContext)[]
> = {}
```
- 读操作的上下文修改先排队
- 等所有读操作完成后统一应用
- 保证写操作的顺序正确

## Claude Code 的关键设计

```typescript
for (const { isConcurrencySafe, blocks } of partitionToolCalls(...)) {
  if (isConcurrencySafe) {
    // 并发执行读操作
    for await (const update of runToolsConcurrently(...)) {
      // 收集上下文修改
    }
    // 统一应用修改
    for (const block of blocks) {
      const modifiers = queuedContextModifiers[block.id]
      // apply modifiers
    }
  } else {
    // 串行执行写操作
    for await (const update of runToolsSerially(...)) {
      // ...
    }
  }
}
```

## 与 OpenClaw 的整合

### OpenClaw 工具分类

**读操作（可并发）：**
- `read` / 文件读取
- `exec`（只读命令）
- `web_fetch` / `web_search`
- `memory_search`
- `sessions_list` / `sessions_history`

**写操作（必须串行）：**
- `write` / `edit`
- `exec`（写命令）
- `message` 发送
- `exec` 文件修改
- `sessions_send`

**混合操作（需判断）：**
- `exec` — 需要看具体命令
- `git` — 读操作多，但 push 是写

### 并发执行方案

```typescript
// 伪代码
async function executeTools(toolCalls: ToolCall[]) {
  const readCalls = toolCalls.filter(isReadOnly)
  const writeCalls = toolCalls.filter(isWrite)

  // 并发执行读操作
  const readResults = await Promise.all(
    readCalls.map(call => executeTool(call))
  )

  // 收集上下文修改
  const contextMods = readResults.map(r => r.contextModifier)

  // 串行执行写操作
  for (const call of writeCalls) {
    await executeTool(call)
  }

  // 统一应用上下文修改
  applyContextModifiers(contextMods)
}
```

## 熔断与限流

### 并发限制
- 默认最大并发：5（保守）
- 读操作：可并发 5-10 个
- 写操作：串行

### 资源感知
```typescript
// 接近资源上限时主动降载
if (isNearResourceLimit()) {
  reduceConcurrency()
}
```

## 核心原则

1. **读可并发，写须串行**
2. **上下文修改排队处理**
3. **有最大并发数限制**
4. **资源接近上限时主动降载**
5. **不是所有工具都适合并发**

## 注意事项

- `exec` 需要判断是读还是写命令
- 网络工具（web_fetch）并发太大会被限流
- 文件写入必须串行保证顺序
- 日志写入需要串行

---
*整合自 Claude Code toolOrchestration.ts 模块，2026-04-07*
