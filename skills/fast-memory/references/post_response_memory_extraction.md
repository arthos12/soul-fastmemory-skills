# Post-Response Memory Extraction（响应后自动记忆提取）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/services/extractMemories/extractMemories.ts`

## 核心机制

### 触发时机
- 每次模型产生最终响应（没有 tool call 时）后触发
- 不是每次回答，而是每个"完整交互回合"结束后
- 由 stopHooks 触发（见 `query/stopHooks.ts`）

### Forked Agent 模式
```typescript
// 用 runForkedAgent 复制当前对话
// 共享主 agent 的 prompt cache
const { runForkedAgent } = require('../utils/forkedAgent.js')
```
- 主 agent 继续处理用户请求
- 分叉出一个"影子 agent"做记忆提取
- 共享上下文，高效且不影响主流程

### 两段式写入
```
第一步：读
- 批量读取所有可能需要更新的记忆文件
- 并行读，不占用主 token 预算

第二步：写
- 基于读取内容判断是否需要更新
- 独立文件写入（user_xxx.md, feedback_xxx.md）
- 最后更新 MEMORY.md 索引
```

### 记忆类型（四分类）
- user — 用户信息
- feedback — 反馈
- project — 项目
- reference — 参考

### 写入规则
```typescript
// 关键规则
1. 只从最新的 N 条消息提取，不浪费 token 调查验证
2. 不重复写入：先检查是否已有相关记忆，有则更新，不新建
3. 语义分类存储：按主题而非时间组织
4. 更新或删除错误/过期的记忆
```

## 实现方案

### OpenClaw 版本

**触发时机：**
- 每次产生最终文本回复后
- 没有 pending tool calls 时
- 非心跳/非轮询请求

**执行流程：**
```
1. 触发条件满足
2. 后台启动"记忆提取 agent"（forked 方式）
3. 读取当前最近的记忆文件
4. 分析最新对话内容
5. 判断是否有值得保存的信息
6. 有则写入对应类型文件 + 更新索引
7. 主 agent 不等待，完成即继续
```

**存储结构：**
```
memory/
  user/           # 用户层
  feedback/      # 反馈层
  project/       # 项目层
  reference/     # 参考层
  MEMORY.md      # 索引（每条 <=150 chars）
```

### 与现有 Fast-Memory 的整合

现有系统已有：
- 分层存储（长期/近期/日志/缓冲）
- S/A/B 保存分级
- 防污染规则

新增：
- 自动触发机制
- forked 后台执行
- 四分类存储
- 索引自动更新

## 核心原则

1. **不阻断主流程** — 记忆提取在后台，不影响响应速度
2. **不浪费 token** — 只分析最新消息，不深入调查
3. **不重复存储** — 先检查再写入
4. **自动维护索引** — MEMORY.md 始终是最新的

---
*整合自 Claude Code extractMemories.ts 模块，2026-04-07*
