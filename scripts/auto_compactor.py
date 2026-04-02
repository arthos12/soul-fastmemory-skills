#!/usr/bin/env python3
"""
auto_compactor.py — 极简版
daily note > 200 行则合并到月度摘要
"""
import sys
from pathlib import Path
from datetime import datetime

MEM = Path("/root/.openclaw/workspace/memory")

def get_topic(name):
    """从文件名提取主题"""
    if "_" in name:
        return name.split("_", 1)[1].replace(".md", "")
    return name.replace(".md", "")

def needs_merge(f):
    """是否需要合并"""
    try:
        lines = sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))
        return lines > 200
    except:
        return False

def get_month(f):
    """获取年月"""
    return f.stem[:7]  # "2026-03"

def generate_summary(files, month):
    """生成月度摘要"""
    sections = [f"# {month} 月度摘要\n"]
    sections.append(f"\n## 来源\n")
    for f in sorted(files):
        sections.append(f"- {f.name}\n")
    sections.append(f"\n## 关键结论\n")
    for f in sorted(files):
        content = f.read_text(encoding="utf-8", errors="ignore")
        # 提取标题和结论行
        for line in content.split("\n"):
            if line.strip() and (line.startswith("#") or any(k in line for k in ["确认", "决定", "结论", "✅", "❌", "完成", "新增", "更新"])):
                sections.append(f"  {line.strip()[:100]}\n")
    return "".join(sections)

def add_backlink(f, summary_name):
    """追加尾注"""
    try:
        c = f.read_text(encoding="utf-8", errors="ignore")
        if f"# ▶ merged" not in c:
            f.write_text(c + f"\n# ▶ merged: {summary_name}\n", encoding="utf-8")
    except:
        pass

def run(dry=False):
    files = list(MEM.glob("????-??-??*.md"))
    by_month = {}
    for f in files:
        if f.name == "compaction_log.md": continue
        m = get_month(f)
        by_month.setdefault(m, []).append(f)

    for month, flist in sorted(by_month.items()):
        big = [f for f in flist if needs_merge(f)]
        if not big:
            print(f"  {month}: ✅ 无需合并")
            continue

        summary_name = f"{month}_summary.md"
        summary_path = MEM / summary_name

        if dry:
            print(f"  {month}: 将合并 {len(big)} 个文件 → {summary_name}")
            continue

        # 生成摘要
        content = generate_summary(big, month)
        summary_path.write_text(content, encoding="utf-8")

        # 加尾注
        for f in big:
            add_backlink(f, summary_name)

        print(f"  {month}: ✅ 合并 {len(big)} → {summary_name}")

if __name__ == "__main__":
    dry = "--dry" in sys.argv
    print(f"\n{'='*40}")
    print(f"Auto Compactor {'(dry-run)' if dry else ''} — {datetime.now().strftime('%H:%M')}")
    print(f"{'='*40}")
    run(dry=dry)
