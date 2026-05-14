# Self-Update Engine — 安装指南

## 步骤 1：确认启动文件

找到你的 agent 启动文件（通常是下列之一）：

- `NEW_SESSION_BOOT.md` — 会话启动序列
- `SOUL.md` — 身份与核心原则
- `CORE_PRINCIPLES.md` — 执行原则
- Claude Code 项目中的 `CLAUDE.md`
- 其他在每次会话开始时自动注入的文件

**如果没有启动文件：** 先创建一个，把"每次都该生效的规则"写进去。这是本 skill 发挥作用的前提。

---

## 步骤 2：在启动文件中加入 Session Protocol

在你的启动文件中添加以下结构（根据你的项目调整文件名）：

```markdown
## Session Protocol

### 记忆自我更新原则

**记方法，不记结果。** 以下事项发生时，立即更新对应文件：

| 触发事项 | 立即更新 |
|---------|---------|
| 写代码发现新规律或踩坑 | `memory/feedback.md` 或类似文件 |
| 分析框架/方法论有新认知 | `memory/methodology.md` 或类似文件 |
| 用户纠正了你的方法 | 同上 |
| SOP 本身需要优化 | 本启动文件 |

**新规则写到哪里：**

| 规则每次都该生效？ | 是 → 本启动文件 |
| 是背景/历史/推导？ | 是 → 专题记忆文件 |

### 任务前加载

**[任务类型 A] 开始前：**
- Read memory/methodology.md
- Read memory/feedback.md

**[任务类型 B] 开始前：**
- Read memory/task_specific.md
```

---

## 步骤 3：建立专题记忆文件

为你的项目创建分类记忆文件，至少包含：

```
memory/
  feedback.md       ← 编码规范、踩坑记录、用户偏好
  methodology.md    ← 分析框架、方法论原则
  tasks.md          ← 任务进度
docs/
  lessons.md        ← 方法论教训、复盘记录
```

每个文件的条目格式：
```markdown
- **规则/方法**：...
  **Why:** 为什么这样（踩坑原因/用户明确说明）
  **How to apply:** 在什么场景下生效
```

---

## 步骤 4（可选）：配置 Stop Hook

如果你的工具链支持 Hook（如 Claude Code），配置 Stop Hook 以在文件有改动时提醒更新记忆：

```python
# hooks/memory_check.py
import subprocess, sys, io

stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def has_changes():
    r = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd="YOUR_PROJECT_PATH", capture_output=True, timeout=5)
    if r.returncode == 1: return True
    u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd="YOUR_PROJECT_PATH", capture_output=True, text=True, timeout=5)
    return bool(u.stdout.strip())

REMINDER = """
+--------------------------------------------------+
|  [记忆自检] 检测到文件有改动                     |
|  这次会话里，有没有需要沉淀到记忆的内容？        |
|                                                  |
|  □ 发现新规律？  → memory/feedback.md           |
|  □ 方法论更新？  → memory/methodology.md        |
|  □ 有验证判断？  → docs/accuracy_log.md         |
|                                                  |
|  有 → 更新记忆   没有 → 忽略                    |
+--------------------------------------------------+
"""

if has_changes():
    stderr.write(REMINDER)
    stderr.flush()
```

**注意：** Hook 只能拦截工具调用，不能约束推理行为。真正的行为约束必须通过启动文件内容实现。

---

## 与 fast-memory 集成

如果已安装 `fast-memory` skill，两者配合如下：

| fast-memory 负责 | self-update-engine 负责 |
|-----------------|------------------------|
| 分层存储（长期/短期） | 检测新认知触发更新 |
| 会话恢复（快速加载） | 判断写到规则引擎还是知识库 |
| 内容分级（1-6 级） | 确保规则真正约束行为 |
| 防污染（不写噪音） | 要求写 Why + How |

建议：`fast-memory` 处理存储生命周期，`self-update-engine` 处理更新决策和约束闭环。

---

## 验收测试

安装完成后，验证以下行为：

1. **发现新认知时**：agent 立即更新对应文件，不等到会话结束
2. **新规则写入时**：agent 判断是进启动文件还是专题记忆文件，不全部写在一个地方
3. **每条记忆**：包含"是什么 + 为什么 + 如何执行"，不只有规则本身
4. **任务开始时**：agent 加载对应类型的专题记忆
5. **完成声明**：agent 运行验证命令后才说完成，不说"应该可以"
