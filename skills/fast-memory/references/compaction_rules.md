# Compaction Rules — 基于 LCM fanout 思想

## 定位
本文件定义了 fast-memory 系统的自动压缩触发规则、溯源格式标准、和还原能力规范。
融合了 Lossless Claw (LCM) 的 DAG 分层压缩思想，但运行在应用层而非系统层。

---

## 一、触发规则（Fanout Triggers）

### 1.1 量化阈值

| 触发条件 | 阈值 | 动作 |
|---|---|---|
| 单个 daily note 行数 | > 200 行 | 标记待合并 |
| `memory/` 同主题文件数 | ≥ 5 个 | 触发合并压缩 |
| `MEMORY.md` 总行数 | > 500 行 | 触发精简扫描 |
| 单个 task/ 项目文件数 | ≥ 8 个 | 触发项目级压缩 |

### 1.2 触发检测（由 auto_compactor.py 执行）

```
check_compaction_needed():
  for each memory/YYYY-MM-DD*.md:
    if lines > 200 → mark pending_merge
  for each unique topic in memory/:
    if file_count >= 5 → trigger topic_compaction
  if MEMORY.md lines > 500 → trigger MEMORY_compact
```

### 1.3 触发频率限制
- 同一文件/主题，两次压缩间隔 ≥ 24 小时（防止频繁重写）
- 每次 session 最多触发 2 次压缩（防止资源过度占用）

---

## 二、压缩层级（DAG Structure）

### 2.1 三层结构

```
Layer 0 (leaf)     : 原始记录 memory/YYYY-MM-DD*.md
Layer 1 (condensed): 主题合并摘要 memory/YYYY-MM-DD_<topic>_summary.md
Layer 2 (root)     : 领域级摘要 references/<domain>_digest.md
```

### 2.2 fanout 规则

| 层级 | 最小 fanout | 最大 fanout | 摘要目标行数 |
|---|---|---|---|
| leaf → condensed | 合并 ≥ 3 个 leaf 文件 | 上限 20 个 | 50–150 行 |
| condensed → root | 合并 ≥ 3 个 condensed 摘要 | 上限 10 个 | 100–300 行 |

---

## 三、双向溯源链格式

### 3.1 摘要文件头格式（必须包含）

```markdown
# SUMMARY: <主题名称>
# created: <YYYY-MM-DD>
# level: condensed|root
# sources: <原文件1>, <原文件2>, <原文件3>
# merged_at: <timestamp>
# reason: fanout≥N | size_overflow | manual_trigger
```

### 3.2 摘要文件体结构

```markdown
## 原始记录摘要
（按时间顺序，保留关键事实）

## 关键提炼
- 结论/决策 1：...
- 结论/决策 2：...

## 未合并细节（保留原始引用路径）
如需查看完整原始上下文：
  grep "<关键词>" <source_file1>
  grep "<关键词>" <source_file2>
```

### 3.3 被合并原文件的尾注格式

在每个被合并进摘要的原始文件**末尾**追加：

```markdown

---

<!-- 🔗 merged_into: memory/YYYY-MM-DD_<topic>_summary.md -->
<!-- merged_at: <timestamp> -->
<!-- reason: fanout≥5 | size_overflow -->
<!-- to_restore: grep "<相关关键词>" memory/YYYY-MM-DD_<topic>_summary.md -->
```

### 3.4 溯源链验证

压缩完成后，必须验证：
1. 所有 source 文件都已加尾注
2. 摘要文件的 sources 列表与实际合并文件一致
3. 关键词路径可还原（抽检 grep 能命中）

---

## 四、还原能力（Expand）

### 4.1 还原原则

摘要永远不能覆盖原始记录。还原时：
1. 先读摘要，获取主题概览
2. 根据摘要中的 `to_restore` grep 指令，从原始文件提取细节
3. 还原是**读操作**，不修改任何文件

### 4.2 还原格式

给定关键词 K，还原链路：

```
memory/YYYY-MM-DD_<topic>_summary.md
  → sources: [file_A, file_B, file_C]
  → grep "K" file_A, file_B, file_C
  → 拼装完整上下文
```

### 4.3 手动还原命令（供 agent 直接使用）

```bash
# 还原某个主题的完整上下文
python scripts/memory_expand.py --topic "<主题>" --query "<关键词>"

# 列出某个摘要的所有原始来源
grep "^# sources:" memory/YYYY-MM-DD_<topic>_summary.md
```

---

## 五、压缩安全规则

### 5.1 删除原始文件的前置条件

只有满足以下**全部条件**，才允许删除原始文件：

- [ ] 该文件已合并进上一层摘要
- [ ] 摘要文件已通过溯源链验证
- [ ] 距离文件最后访问已超过 7 天
- [ ] 该文件不在当前 active session 的恢复路径上
- [ ] 备份副本已写入 `memory/archive/` 目录

### 5.2 删除后的日志

删除操作必须在 `memory/archive/compaction_log.md` 中记录：

```markdown
## <timestamp> 删除记录
- deleted: memory/YYYY-MM-DD_xxx.md
- merged_into: memory/YYYY-MM-DD_<topic>_summary.md
- reason: fanout≥5, verified, archived
- backup: memory/archive/YYYY-MM-DD_xxx.md.bak
```

### 5.3 禁止行为

- ❌ 禁止在未生成摘要前删除原始文件
- ❌ 禁止跳过溯源链验证直接删除
- ❌ 禁止在 active session 期间删除任何文件
- ❌ 禁止用压缩替代记忆写入（压缩是整理，不是写入）

---

## 六、与 hourly_work.py 的集成

在 `hourly_work.py` 中加入检查项：

```python
# === Compaction Check ===
def check_compaction():
    """检查是否需要压缩，每小时最多执行一次"""
    # 1. 检查 daily notes 行数
    # 2. 检查同主题文件 fanout
    # 3. 检查 MEMORY.md 行数
    # 4. 如触发阈值，执行 auto_compactor.py
```

集成时机：每次 hourly_work 运行时，顺便检查 compaction，不需要独立调度。

---

## 七、配置参数（Defaults，可覆盖）

| 参数 | 默认值 | 说明 |
|---|---|---|
| `MAX_DAILY_LINES` | 200 | 超过此行数触发标记 |
| `MIN_FANOUT_LEAF` | 3 | leaf→condensed 最小合并数 |
| `MIN_FANOUT_ROOT` | 3 | condensed→root 最小合并数 |
| `MAX_FANOUT` | 20 | 单次合并最大文件数 |
| `COMPACT_INTERVAL_H` | 24 | 同一文件两次压缩最小间隔（小时） |
| `MAX_COMPACTION_PER_SESSION` | 2 | 单 session 最多压缩次数 |
| `ARCHIVE_RETENTION_DAYS` | 7 | 删除前保留备份的天数 |
| `SUMMARY_TARGET_LINES` | 50–150 | condensed 摘要目标行数 |
| `ROOT_SUMMARY_TARGET_LINES` | 100–300 | root 摘要目标行数 |
