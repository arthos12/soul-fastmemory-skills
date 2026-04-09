# Google "Introduction to Agents" 白皮书摘要

> 来源：Google Cloud AI 团队（Alan Blount, Antonio Gulli, Shubham Saboo, Michael Zimmermann, Vladimir Vuskovic）
> 发布时间：2025年11月
> 性质：54页生产级 Agent 架构技术白皮书
> 另有一份「AI Agent Handbook」为业务推广版，内容不同

---

## 一、核心架构（四件套）

| 组件 | 角色 | 作用 |
|---|---|---|
| Model | 大脑 | 推理引擎，处理信息做决策 |
| Tools | 手 | 连接外部世界：API、代码函数、数据库 |
| Orchestration | 神经系统 | 编排层，管理 Planning→Memory→推理策略→执行循环 |
| Deployment | 身体+腿 | 生产级托管、监控、日志、管理服务 |

**核心定义**：Agent = Model + Tools + Orchestration + Deployment，通过 LLM 循环完成目标。

---

## 二、开发者角色转变

- **传统开发者** = 泥水匠（bricklayer），精确砌每一步逻辑
- **Agent 开发者** = 导演（director）：给场景（指令）、选演员（工具/API）、喂背景（数据），让自主演员自己演

**一个核心观点**：Agent 是「上下文窗口策展的艺术」——不断循环：装配上下文 → 调用模型 → 观察结果 → 重新装配。

---

## 三、Agent 解决问题五步循环

```
1. Get Mission（接任务）
   ↓
2. Scan the Scene（感知环境：用户请求+短期记忆+工具）
   ↓
3. Think It Through（核心推理：分析任务+制定计划）
   ↓
4. Take Action（调用 API / 执行函数 / 查询数据库）
   ↓
5. Observe & Iterate（观察结果，加入上下文，循环直到目标达成）
```

---

## 四、Agent 能力五级分类

| 级别 | 名称 | 描述 |
|---|---|---|
| L0 | 核心推理 | 纯模型，靠预训练知识，无实时信息 |
| L1 | 连接工具 | 能调用搜索 API / 金融 API / RAG 数据库 |
| L2 | 战略规划 | 复杂多步任务，主动上下文工程（Context Engineering） |
| L3 | 多 Agent 协作 | 多个 Agent 分工协作 |
| L4 | 自我进化 | 能自主训练、自我改进（最顶级） |

---

## 五、实战案例（客服 Agent）

用户问："我的订单 #12345 到哪了？"

**Think 阶段**：
- 识别：在数据库里找订单
- 跟踪：提取快递号，查询物流 API
- 报告：汇总成用户语言

**执行循环**：
- Act: find_order("12345") → 观察到订单记录，快递号 "ZYX987"
- Act: get_shipping_status("ZYX987") → 观察到 "派送中"
- Report: "您的订单 #12345 正在派送中！"

---

## 六、关键结论

1. **Agent 是 LLM 的进化形态**：不是静态工作流，而是能用工具在环境中自主循环执行目标的完整应用
2. **核心能力 = 上下文工程**：Agent 的质量取决于每次往上下文窗口里塞什么
3. **开发范式转移**：从「定义每一步」到「定义目标+工具+上下文，让 Agent 自己规划路径」
4. **L4 是最终形态**：能自我训练、自我修复、自主进化

---

## 相关文件

- 原始 PDF（54页）：`https://services.google.com/fh/files/misc/ai_agents_handbook.pdf`
- 备份 PDF（另一源）：`https://www.hkdca.com/wp-content/uploads/2025/11/introduction-to-agents-google.pdf`
- 摘要页：`http://vanducng.dev/2026/01/10/Google-Introduction-to-Agents-Whitepaper-Summary/`
