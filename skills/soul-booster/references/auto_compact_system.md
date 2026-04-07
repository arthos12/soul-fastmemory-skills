# Auto Compact System（自动上下文压缩）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/compact/autoCompact.ts`

## 核心机制

### 触发条件
- 监控当前上下文 token 使用量
- 达到阈值时自动触发压缩
- 可配置触发窗口（通过环境变量）

### 熔断机制
```typescript
consecutiveFailures?: number  // 连续失败计数
```
- 连续失败超过阈值后停止重试
- 防止无限重试消耗资源

### 输出预算
- 保留 20,000 tokens 给输出预算
- 压缩后的摘要和原始内容有比例控制

## Claude Code 的关键设计

```typescript
// 保留输出预算
const MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000

// 有效上下文窗口 = 总窗口 - 输出预算
export function getEffectiveContextWindowSize(model: string): number {
  const contextWindow = getContextWindowForModel(model)
  return contextWindow - reservedTokensForSummary
}
```

### 触发状态追踪
```typescript
export type AutoCompactTrackingState = {
  compacted: boolean        // 是否已压缩
  turnCounter: number      // 轮次计数
  turnId: string          // 每轮唯一ID
  consecutiveFailures?: number  // 连续失败（熔断用）
}
```

## 压缩类型（从 compact.ts 可见）

1. **apiMicrocompact** — API 级别微压缩
2. **microCompact** — 微压缩
3. **sessionMemoryCompact** — Session 记忆压缩
4. **timeBasedMC** — 基于时间的压缩
5. **postCompactCleanup** — 压缩后清理

## 与现有系统对比

| Claude Code | OpenClaw 当前 |
|-------------|--------------|
| 自动监控 token | 手动清理 session |
| 无感知压缩 | 需人工触发 |
| 熔断保护 | 无 |
| 输出预算控制 | 无 |

## 借鉴到 OpenClaw

### 设计方案

**触发条件：**
- 上下文超过 80% 阈值时触发
- 保留 5000 tokens 输出预算
- 连续失败 3 次后熔断

**压缩流程：**
```
1. 识别当前上下文使用量
2. 达到阈值 → 触发压缩
3. 压缩前保存关键状态（主线、下一步、阻塞）
4. 执行压缩（保留关键记忆）
5. 压缩后清理临时数据
6. 若失败 → 记录失败计数，触发熔断
```

**状态文件：**
```json
{
  "compacted": false,
  "turnCounter": 0,
  "consecutiveFailures": 0,
  "lastCompactedAt": null
}
```

## 核心原则

1. **压缩不是删除** — 是提炼，不是丢弃
2. **保留核心** — 主线、下一步、关键结论必须保留
3. **有熔断** — 连续失败后停止，防止空转
4. **有输出预算** — 保证压缩后还有输出空间

---
*整合自 Claude Code autoCompact.ts 模块，2026-04-07*
