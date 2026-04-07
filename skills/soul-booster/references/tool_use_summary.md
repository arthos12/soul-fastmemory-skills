# Tool Use Summary（工具执行摘要）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/toolUseSummary/toolUseSummaryGenerator.ts`

## 核心机制

### 目标
用轻量模型（Haiku）为工具执行生成简洁的人类可读摘要。

### 设计原则
```
格式要求：
- 30 字符以内
- git commit 风格
- 动词用过去式
- 保留最具区分性的名词
- 去掉冠词、连词和长路径上下文

示例：
- "Searched in auth/"
- "Fixed NPE in UserService"
- "Created signup endpoint"
- "Read config.json"
- "Ran failing tests"
```

### Claude Code 实现
```typescript
const TOOL_USE_SUMMARY_SYSTEM_PROMPT = `Write a short summary label describing what these tool calls accomplished. It appears as a single-line row in a mobile app and truncates around 30 characters, so think git-commit-subject, not sentence.

Keep the verb in past tense and the most distinctive noun. Drop articles, connectors, and long location context first.`

type ToolInfo = {
  name: string
  input: unknown
  output: unknown
}

export async function generateToolUseSummary({
  tools,
  signal,
  isNonInteractiveSession,
  lastAssistantText,
}): Promise<string | null> {
  // 1. 收集工具信息
  // 2. 调用 Haiku 生成摘要
  // 3. 截断到 30 字符
}
```

## OpenClaw 版本设计

### 实现方案
```python
# 伪代码
async def generate_tool_summary(tools: list[ToolCall]) -> str:
    """
    工具执行后生成简洁摘要
    """
    summaries = []
    for tool in tools:
        summary = summarize_tool(tool)
        summaries.append(summary)
    
    # 合并多个工具的摘要
    return " | ".join(summaries[:3])  # 最多 3 个

def summarize_tool(tool: ToolCall) -> str:
    """将工具调用转换为 30 字以内的摘要"""
    name = tool.name
    # 根据工具类型生成对应摘要
    
    # read → "Read {filename}"
    # write → "Wrote {filename}"
    # exec → "Ran command"
    # search → "Searched for {query}"
    
    return truncated_summary
```

### 摘要规则

| 工具类型 | 摘要格式 | 示例 |
|---------|---------|------|
| read | "Read {filename}" | "Read config.json" |
| write | "Wrote {filename}" | "Wrote results.md" |
| edit | "Edited {filename}" | "Edited main.py" |
| exec | "Ran command" | "Ran tests" |
| web_fetch | "Fetched {domain}" | "Fetched github.com" |
| search | "Searched {query}" | "Searched Python docs" |

### 集成到响应

```
当前 OpenClaw 输出：
[Tool] read file: /root/.openclaw/workspace/MEMORY.md
文件内容：...

带摘要版本：
✓ Read MEMORY.md (2.3KB)
```

## 与现有系统的整合

### 适用场景
- 工具执行后的输出展示
- 多步骤任务的进度汇报
- 结果摘要替换长输出

### 不适用场景
- 错误信息（需要完整输出）
- 调试场景（需要完整结果）
- 用户明确要求看完整输出

## 核心原则

1. **简洁优先** — 30 字符以内
2. **可逆** — 用户问"详情"可展开
3. **不丢失关键信息** — 摘要要包含文件名/关键值
4. **不暴露敏感** — 摘要不包含 token/密码等

---
*整合自 Claude Code toolUseSummaryGenerator.ts 模块，2026-04-07*
