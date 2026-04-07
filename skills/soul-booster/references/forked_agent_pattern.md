# Forked Agent Pattern（分支 Agent 模式）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/utils/forkedAgent.js`

## 核心机制

### 什么是 Forked Agent
在主 agent 处理请求的同时，分叉出一个"影子 agent"执行后台任务。
影子 agent 共享主 agent 的 prompt cache，高效且不干扰主流程。

### Claude Code 的实现

```typescript
// runForkedAgent 核心逻辑
async function runForkedAgent(options: ForkedAgentOptions) {
  // 1. 复制当前对话上下文
  const forkedContext = duplicateContext(mainContext)

  // 2. 共享 prompt cache（关键优化）
  forkedContext.promptCache = mainContext.promptCache

  // 3. 后台执行任务
  return await agent.run(forkedContext, {
    background: true,
    onComplete: (result) => {
      // 任务完成后回调
      mergeResult(result)
    }
  })
}
```

### 使用场景（从源码可见）

1. **记忆提取**（extractMemories）
   - 主 agent 继续回答用户
   - 影子 agent 提取记忆

2. **后台记忆整合**（autoDream）
   - 空闲时整合多个 session
   - 不占用主流程

3. **任务完成后钩子**（stopHooks）
   - 执行完成后的清理/归档

### Fork vs Subagent

| 维度 | Forked Agent | Subagent |
|------|---------------|----------|
| 上下文 | 共享主 agent 的 | 独立新建 |
| 资源消耗 | 低（共享 cache） | 高（独立加载） |
| 适用场景 | 轻量后台任务 | 独立复杂任务 |
| 响应速度 | 不影响主响应 | 可能延迟 |

### OpenClaw 版本设计

#### 实现方式
```python
# 伪代码
async def fork_background_task(main_task, background_fn):
    """
    主 agent 继续执行 main_task
    同时启动 background_fn()
    """
    # 1. 主 agent 执行主任务
    main_result = await main_task()

    # 2. 启动后台任务（不等待）
    background_task = asyncio.create_task(background_fn())

    return main_result
```

#### 共享上下文优化
```
OpenClaw 版本优化：
1. 读取主 session 的关键状态
2. 后台任务继承该状态（不复制完整历史）
3. 减少内存占用
```

#### 使用场景

1. **记忆提取**
   ```python
   async def on_response_complete(response):
       if response.is_final and not response.has_tool_calls:
           # 启动记忆提取后台任务
           asyncio.create_task(extract_memories(response))
   ```

2. **定时任务**
   ```python
   # 每小时检查一次
   async def hourly_maintenance():
       await check_runner_status()
       await cleanup_old_sessions()
       await extract_memories_from_idle_sessions()
   ```

3. **长任务分解**
   ```python
   async def execute_large_task(task):
       # 主 agent 处理用户交互
       # 后台 agent 处理耗时操作
       parts = split_task(task)
       for part in parts:
           await execute(part)
           await yield_to_main()  # 让主 agent 有机会响应
   ```

## 核心原则

1. **不阻塞主流程** — 后台任务不延迟主响应
2. **共享优化** — 复用上下文，减少资源
3. **可取消** — 主任务结束，后台任务也应清理
4. **独立错误处理** — 后台任务失败不影响主流程

## 实现注意事项

### 资源控制
- 同时最多 N 个后台任务
- 超出排队或丢弃
- 监控内存/CPU 使用

### 错误处理
```python
try:
    await background_task
except Exception as e:
    log_error(f"Background task failed: {e}")
    # 不传播到主流程
```

### 取消传播
```python
# 主任务取消时
if main_task.is_cancelled():
    background_task.cancel()
    await background_task  # 等待清理完成
```

---
*整合自 Claude Code forkedAgent.ts 模块，2026-04-07*
