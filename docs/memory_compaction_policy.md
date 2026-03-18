# Memory Compaction Policy

## 目标
- 控制 session 相关文件体积，降低上下文长度与 token 消耗。
- 不做破坏性删除，先做检测与压缩提示。

## 触发阈值（可调）
- MEMORY.md > 40KB
- LAST_SESSION.md > 25KB
- SESSION_HANDOFF.md > 12KB
- daily memory file > 20KB

## 动作
1. 生成体积报告（data/memory_compact/report.json）
2. 超阈值时写入建议（data/memory_compact/alerts.jsonl）
3. 默认不删除，仅提示压缩/迁移

## 压缩策略
- MEMORY.md：只保留长期规则与稳定偏好，去掉临时细节
- LAST_SESSION/SESSION_HANDOFF：只保留主线、下一步、阻塞、关键文件
- daily log：保留当天关键结论，其余降级为一句摘要
