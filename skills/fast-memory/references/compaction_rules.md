# Compaction Rules（极简版）

## 触发
- 单个 daily note > 200 行 → 合并

## 合并格式
```
# <YYYY-MM> 月度摘要

## 来源
- memory/2026-03-16.md
- memory/2026-03-20.md

## 关键结论
- ...

## 待查细节
grep "<关键词>" memory/2026-03-16.md
```

## 合并后
- 原始文件加一行尾注：`# ▶ merged: memory/YYYY-MM_summary.md`
- 不删原始文件，只做引用合并
