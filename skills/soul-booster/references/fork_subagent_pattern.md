# Fork Subagent Pattern（隐式分叉 Agent）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/tools/AgentTool/forkSubagent.ts`

## 核心机制

### 什么是 Fork Subagent
当用户不指定 subagent_type 时，自动触发 fork：
- 子 agent 继承父 agent 的完整上下文
- 继承 system prompt
- 共享 prompt cache
- 后台异步执行

### 关键设计

```typescript
// 不指定 subagent_type 时触发 fork
const FORK_AGENT = {
  tools: ['*'],           // 继承父 agent 的工具池
  model: 'inherit',       // 继承父 agent 的模型
  permissionMode: 'bubble'  // 权限提示回到父终端
}

// fork 后系统 prompt 的传递方式
// 不调用 getSystemPrompt()，直接 thread renderedSystemPrompt
// 因为 GrowthBook 可能导致 cold→warm 状态变化，破坏 prompt cache
```

### 与显式 Subagent 的区别

| 维度 | Fork Subagent | 显式 Subagent |
|------|---------------|---------------|
| 上下文 | 继承父的完整上下文 | 独立新建 |
| System Prompt | 共享渲染后的 | 需要重新获取 |
| Prompt Cache | 共享（高效） | 不共享（浪费） |
| 触发方式 | 不指定 type 时自动 | 显式创建 |
| 适用场景 | 轻量后台任务 | 独立复杂任务 |

### 权限处理
```typescript
permissionMode: 'bubble'
// 子 agent 的权限请求会"冒泡"到父终端
// 用户在父终端批准，子 agent 继续执行
```

## Claude Code 的使用场景

```typescript
// 当用户输入 /fork <directive> 时
// 创建一个隐式分叉

// 示例：
// 用户输入 /fork帮我查一下这个项目用了什么框架
// → 创建 fork subagent
// → 继承当前对话上下文
// → 后台执行查询
// → 返回结果到主对话
```

## OpenClaw 版本设计

### 触发条件
```python
# 以下情况触发隐式分叉：
# 1. 调用工具时不指定具体 agent
# 2. 父 agent 产生响应后，后台任务需要继续执行
# 3. 记忆提取、整合等后台任务

async def execute_background_task(task_fn):
    """
    执行后台任务，自动 fork
    """
    # 创建 forked context
    forked_ctx = fork_context(parent_ctx)
    
    # 共享 prompt cache
    forked_ctx.prompt_cache = parent_ctx.prompt_cache
    
    # 后台执行
    result = await task_fn(forked_ctx)
    
    return result
```

### 上下文继承
```python
def fork_context(parent):
    return {
        "messages": parent.messages,  # 完整消息历史
        "system_prompt": parent.rendered_system_prompt,  # 已渲染的
        "tools": parent.tools,  # 工具列表
        "memory": parent.memory,  # 记忆引用
        "config": parent.config,  # 配置
        # 不复制：运行状态、中断信号等
    }
```

### 与 Forked Agent Pattern 的关系

| 维度 | Fork Subagent | Forked Agent |
|------|---------------|--------------|
| 来源 | Agent Tool 的隐式分叉 | 通用后台任务模式 |
| 触发 | 不指定 type | 显式创建 |
| 上下文 | 继承 + 共享 cache | 继承 + 共享 cache |
| 主要用途 | 工具调用 | 记忆提取/整合 |

两者是同一机制的两种用法。

## 实现注意事项

### 避免循环依赖
```typescript
// forkSubagent.ts 不能导入某些模块，因为会创建循环依赖
// 改用 dependency injection 传递
```

### Prompt Cache 一致性
```typescript
// 错误：重新调用 getSystemPrompt()
// 正确：直接使用 parent.renderedSystemPrompt
```

### 资源控制
```python
# 同时最多 N 个 fork
# 超出排队或拒绝
MAX_CONCURRENT_FORKS = 3
```

## 核心原则

1. **透明分叉** — 用户无感知，后台执行
2. **高效继承** — 共享 cache，不浪费资源
3. **权限冒泡** — 权限请求回到父终端
4. **可中断** — 主任务可取消所有 fork

---
*整合自 Claude Code forkSubagent.ts 模块，2026-04-07*
