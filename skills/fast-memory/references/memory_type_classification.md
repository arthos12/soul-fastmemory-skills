# Memory Type Classification（记忆类型分类）

## 来源
借鉴自 Claude Code v2.1.88 源码 `src/memdir/memoryTypes.ts`

## 四种记忆类型

### Type 1: user（用户层）
**范围**：always private

存储内容：
- 用户角色、目标、职责、知识
- 用户偏好、习惯、表达方式
- 与用户工作风格相关的信息

示例：
```
user: 用户是价值投资者，偏好长期持有，不喜欢追热点
user: 用户容易在 fomo 时做决策，需要冷静期
```

使用场景：
- 回答问题时要考虑用户背景
- 解释概念时要用用户能理解的类比
- 决策时考虑用户的风险偏好

---

### Type 2: feedback（反馈层）
**范围**：private default，team only when 明显是项目级 convention

存储内容：
- 用户给出的反馈（什么该避免、什么该继续做）
- 成功和失败的教训都要记录
- 纠偏后的正确路径

重要原则：
> 如果只记录纠正，会避免过去的错误，但会偏离已经验证过的方法，可能变得过于谨慎。

示例：
```
feedback: 用户说不要追高，已经验证过多次
feedback: 用户认可的方向：先找项目，再找带单方
```

使用场景：
- 做决策前检查是否有相关 feedback
- 避免重复犯同样的错误
- 保持已验证有效的方法

---

### Type 3: project（项目层）
**范围**：private or team depending on project scope

存储内容：
- 项目基本信息、目标、进展
- 项目特有的规则、约束、约定
- 当前阶段、下一步、阻塞点

示例：
```
project: Polymarket 量化项目
- 目标：建立稳定盈利的 5m 市场预测系统
- 当前状态：策略已定，参数优化中
- 下一步：实盘验证
```

使用场景：
- 恢复项目时快速了解状态
- 多 session 推进同一项目
- 项目交接

---

### Type 4: reference（参考层）
**范围**：private or team depending on utility

存储内容：
- 分析框架、方法论
- 数据来源、工具清单
- 可复用的模板、流程

示例：
```
reference: 芒格思维模型框架
reference: BR 对比分析方法
reference: Polymarket 因子库
```

使用场景：
- 快速获取方法论支撑
- 分析问题时调用框架
- 不需要每次重新构建方法

---

## 核心设计原则

### 原则1：只存不能从上下文推导的信息
Claude Code 的原话：
> Memories are constrained to four types capturing context NOT derivable from the current project state. Code patterns, architecture, git history, and file structure are derivable and should NOT be saved as memories.

**Bot 版本：**
- 用户偏好、反馈、项目状态不能从当前上下文直接推导 → 要存
- 已经在当前文件/代码/配置里的信息 → 不存
- 已经能通过工具直接获取的信息 → 不存

### 原则2：反馈要双向记录
- 不仅记录"避免什么"
- 也要记录"什么做对了，应该继续"

### 原则3：记忆分类不是碎片化存储
- 每条记忆要有明确的 type 标签
- 按 type 分类检索，不是按时间检索
- 定期清理错误/过期的记忆

---

## 与现有分层的关系

现有系统用时间分层（长期/近期/日志/缓冲），本模块加内容维度。

| 维度 | 现有分层 | 新增分类 |
|------|----------|----------|
| 时间 | 长期/近期/日志/缓冲 | - |
| 内容 | - | user/feedback/project/reference |

两者结合：
- 时间分层管"多久整理一次"
- 类型分类管"存什么、怎么用"

---

## 保存决策流程

```
收到要保存的信息
→ 判断 type（user/feedback/project/reference）
→ 判断是否已在上下文中（能直接推导的不存）
→ 判断 importance（高价值才存完整，低价值压缩）
→ 写入对应 type 的存储位置
```

## 示例：同一信息，不同处理

**信息**："用户偏好低风险策略，单笔不超过总资金 5%"

| 判断维度 | 结果 |
|----------|------|
| type | user（用户偏好）|
| 是否可推导 | 否（不能从上下文直接得出）|
| importance | 高（影响所有交易决策）|
| 保存完整度 | 完整 |

**信息**："这个文件在 /root/data/ 目录"

| 判断维度 | 结果 |
|----------|------|
| type | 无（可从文件系统中直接获取）|
| 是否可推导 | 是（ls 一下就知道）|
| importance | 低 |
| 保存完整度 | 不存 |

---
*整合自 Claude Code memoryTypes.ts 模块，2026-04-07*
