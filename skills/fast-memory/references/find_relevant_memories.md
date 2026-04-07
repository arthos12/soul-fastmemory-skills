# findRelevantMemories（相关性记忆检索）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/memdir/findRelevantMemories.ts`

## 核心机制

### 问题
长期记忆系统面临的问题：
- 记忆文件越来越多
- 全量加载消耗大量 token
- 大部分记忆与当前 query 无关

### Claude Code 的解决方案
1. 扫描所有记忆文件的头部（header + 前几行）
2. 用轻量模型（Sonnet）选择最相关的 5 个
3. 只加载选中的记忆到上下文

### 关键设计

```typescript
const SELECT_MEMORIES_SYSTEM_PROMPT = `You are selecting memories that will be useful to Claude Code as it processes a user's query. You will be given the user's query and a list of available memory files with their filenames and descriptions.

Return a list of filenames for the memories that will clearly be useful (up to 5).
- If you are unsure if a memory will be useful, do not include it
- If there are no useful memories, return an empty list
- DO NOT select memories that are usage reference or API documentation`
```

### 检索流程
```typescript
export async function findRelevantMemories(
  query: string,
  memoryDir: string,
  signal: AbortSignal,
  recentTools: readonly string[] = [],
  alreadySurfaced: ReadonlySet<string> = new Set(),
): Promise<RelevantMemory[]> {
  // 1. 扫描所有记忆文件
  const memories = await scanMemoryFiles(memoryDir, signal)
  
  // 2. 过滤已展示的
  const filtered = memories.filter(m => !alreadySurfaced.has(m.filePath))
  
  // 3. 用轻量模型选择最相关的
  const selectedFilenames = await selectRelevantMemories(
    query,
    filtered,
    signal,
    recentTools
  )
  
  // 4. 返回路径和 mtime
  return selectedFilenames.map(filename => ({
    path: filename,
    mtime: getMtime(filename)
  }))
}
```

### mtime 追踪
```
返回 mtime 的原因：
- 可以告诉用户记忆的"新鲜度"
- 新的记忆可能更相关
- 避免加载过时的信息
```

## OpenClaw 版本设计

### 实现方案

```python
async def find_relevant_memories(
    query: str,
    memory_dir: str,
    max_count: int = 5
) -> list[dict]:
    """
    根据 query 找到最相关的记忆文件
    """
    # 1. 扫描所有记忆文件
    all_memories = scan_memory_files(memory_dir)
    
    # 2. 生成记忆索引（用于选择）
    memory_manifest = [
        {
            "filename": m.filename,
            "description": extract_header(m),  # 前 100 字符
            "type": extract_type(m)  # user/feedback/project/reference
        }
        for m in all_memories
    ]
    
    # 3. 调用轻量模型选择
    selected = await select_memories(
        query=query,
        memories=memory_manifest,
        max_count=max_count
    )
    
    # 4. 返回路径和元信息
    return [
        {
            "path": find_by_filename(selected),
            "mtime": get_mtime(),
            "type": get_type()
        }
    ]
```

### 索引格式

```yaml
# memory/manifest.json
{
  "memories": [
    {
      "filename": "user_investment_style.md",
      "type": "user",
      "summary": "用户偏好价值投资，不喜欢追热点...",
      "mtime": 1712500000
    },
    {
      "filename": "feedback_polymarket.md", 
      "type": "feedback",
      "summary": "不要追高，已验证多次...",
      "mtime": 1712400000
    }
  ]
}
```

### 与 MEMORY.md 的关系

```
MEMORY.md（索引）：
- [user_investment_style](user_investment_style.md)
- [feedback_polymarket](feedback_polymarket.md)

findRelevantMemories：
- 扫描所有 .md 文件
- 读取 header
- 语义选择最相关的 5 个
```

### 缓存优化

```python
# 记忆文件变化时重建索引
# 索引变化时增量更新
async def rebuild_index_if_needed():
    manifest_path = "memory/manifest.json"
    if is_stale(manifest_path):
        await rebuild_manifest()
```

## 与现有 Fast-Memory 的整合

现有系统已有：
- 四分类存储（user/feedback/project/reference）
- 分层存储（长期/近期/日志/缓冲）

新增：
- 语义检索层
- 索引缓存
- 动态加载

## 核心原则

1. **不全部加载** — 按需加载，最多 5 个
2. **语义选择** — 用模型理解记忆内容
3. **索引加速** — manifest 避免全量扫描
4. **可追溯** — 返回 mtime 保证新鲜度

---
*整合自 Claude Code findRelevantMemories.ts 模块，2026-04-07*
