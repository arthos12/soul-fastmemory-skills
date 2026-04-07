# Background Memory Consolidation（后台记忆整合）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/autoDream/`

## 核心机制

### 灵感来源：人类记忆巩固
人类睡眠时会巩固白天的记忆，将短期记忆转移到长期记忆。
Claude Code 的 autoDream 就是这个原理。

### 触发门控（三个条件，短路求值）

```typescript
// 1. 时间门控
hours since lastConsolidatedAt >= minHours

// 2. 会话数门控
transcript count with mtime > lastConsolidatedAt >= minSessions

// 3. 锁门控
no other process mid-consolidation
```

### 整合流程
```
1. 检查时间门控 → 通过？
2. 检查会话数门控 → 通过？
3. 检查锁 → 无其他进程？
   → 是：获取锁，开始整合
   → 否：跳过，等待下次
4. 读取所有自上次整合后的 session
5. 提取高价值记忆
6. 合并到长期记忆
7. 释放锁
8. 更新时间戳
```

### consolidationLock 机制
```typescript
// 文件锁，防止并发
const lockPath = '.dream/consolidation.lock'
// 获取锁：创建文件，写入 PID
// 释放锁：删除文件
// 异常时：rollback
```

## OpenClaw 版本设计

### 触发条件
```yaml
minHours: 24        # 至少间隔 24 小时
minSessions: 3      # 至少 3 个新 session
```

### 执行流程
```
1. 检查上次整合时间
2. 统计新增 session 数量
3. 满足条件 → 获取锁 → 执行整合
4. 不满足条件 → 跳过
```

### 整合内容
- 多个 session 的高频记忆片段
- 跨 session 的项目连续性
- 用户偏好变化
- 反馈积累

### 锁机制
```python
# 伪代码
import fcntl

lock_file = '.consolidation.lock'
with open(lock_file, 'w') as f:
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        f.write(str(os.getpid()))
        # 执行整合
        fcntl.flock(f, fcntl.LOCK_UN)
    except BlockingIOError:
        # 已有进程在整合，跳过
        pass
```

## 与 Post-Response Memory Extraction 的关系

| 维度 | Post-Response | Background Consolidation |
|------|---------------|-------------------------|
| 时机 | 每次响应后 | 达到阈值后 |
| 内容 | 最新的单次对话 | 跨多个 session |
| 目的 | 快速保存 | 深度整合 |
| 资源 | 轻量 | 重 |

两者配合：
- Post-Response 处理即时记忆
- Consolidation 处理跨周期整合

## 核心原则

1. **不抢占资源** — 后台空闲时执行
2. **可中断** — 锁机制保证可恢复
3. **增量执行** — 只处理新内容
4. **防重复** — 已整合的不再处理

---
*整合自 Claude Code autoDream.ts 模块，2026-04-07*
