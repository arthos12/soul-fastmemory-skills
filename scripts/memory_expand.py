#!/usr/bin/env python3
"""
memory_expand.py — 上下文还原工具

给定关键词/主题，从摘要文件 + 原始文件中
重建完整上下文链（LCM lcm_expand 思路的本地实现）

使用方式:
  python scripts/memory_expand.py --topic "soul-upgrade"
  python scripts/memory_expand.py --query "投资逻辑"
  python scripts/memory_expand.py --list-summaries
  python scripts/memory_expand.py --trace memory/2026-03-20.md
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SKILL_REFS = WORKSPACE / "skills" / "fast-memory" / "references"


# ============================================================================
# 核心函数
# ============================================================================

def list_summaries() -> List[Dict]:
    """列出所有摘要文件及其溯源信息"""
    summaries = []
    if not MEMORY_DIR.exists():
        return summaries
    for f in MEMORY_DIR.glob("*_summary.md"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            header = parse_summary_header(content)
            header["file"] = f.name
            header["size_kb"] = f.stat().st_size // 1024
            summaries.append(header)
        except:
            pass
    return summaries


def parse_summary_header(content: str) -> Dict:
    """解析摘要文件头"""
    header = {
        "topic": "unknown",
        "created": "",
        "level": "",
        "sources": [],
        "merged_at": "",
        "reason": "",
    }
    for line in content.split("\n")[:20]:
        if line.startswith("# sources:"):
            sources_str = line.split(":", 1)[1].strip()
            header["sources"] = [s.strip() for s in sources_str.split(",") if s.strip()]
        elif line.startswith("# SUMMARY:"):
            header["topic"] = line.split(":", 1)[1].strip()
        elif line.startswith("# created:"):
            header["created"] = line.split(":", 1)[1].strip()
        elif line.startswith("# level:"):
            header["level"] = line.split(":", 1)[1].strip()
        elif line.startswith("# merged_at:"):
            header["merged_at"] = line.split(":", 1)[1].strip()
        elif line.startswith("# reason:"):
            header["reason"] = line.split(":", 1)[1].strip()
    return header


def find_summaries_for_topic(topic: str) -> List[Dict]:
    """找到指定主题的所有摘要"""
    summaries = list_summaries()
    return [s for s in summaries if topic.lower() in s.get("topic", "").lower()]


def expand_from_summary(summary: Dict, max_lines: int = 500) -> str:
    """从摘要文件展开，还原完整上下文"""
    summary_path = MEMORY_DIR / summary["file"]
    try:
        content = summary_path.read_text(encoding="utf-8", errors="ignore")
        return content[:max_lines]
    except:
        return f"[无法读取: {summary['file']}]"


def grep_original(source_files: List[str], keyword: str, max_hits: int = 50) -> Dict[str, List[str]]:
    """
    在原始文件中 grep 关键词
    返回 {filename: [matching_lines]}
    """
    results = {}
    for fname in source_files:
        fpath = MEMORY_DIR / fname
        if not fpath.exists():
            # 尝试 archive
            for bak in MEMORY_DIR.glob(f"archive/{fname.stem}_bak_*"):
                fpath = bak
                break
        if not fpath.exists():
            continue
        try:
            lines = fpath.read_text(encoding="utf-8", errors="ignore").split("\n")
            hits = [line.strip() for line in lines if keyword.lower() in line.lower()]
            if hits:
                results[fname] = hits[:max_hits]
        except:
            pass
    return results


def trace_file(file_path: Path) -> Dict:
    """
    追溯一个文件的压缩链：
    它被合并进了哪些摘要？原始来源是？
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except:
        return {"error": f"无法读取 {file_path}"}

    trace = {
        "file": file_path.name,
        "merged_into": [],
        "content_preview": content[:500],
    }

    # 查找 merged_into 尾注
    for line in content.split("\n"):
        if "merged_into:" in line:
            m = re.search(r"merged_into:\s*(.+?)\s*(?:-->)", line)
            if m:
                trace["merged_into"].append(m.group(1).strip())

    # 如果这个文件本身就是摘要，找到它的 sources
    if "_summary.md" in file_path.name:
        header = parse_summary_header(content)
        trace["sources"] = header.get("sources", [])
        trace["topic"] = header.get("topic", "unknown")
        trace["level"] = header.get("level", "")

    return trace


def expand_topic(topic: str, keyword: Optional[str] = None,
                 max_lines: int = 1000) -> str:
    """
    展开某个主题的完整上下文链
    1. 找到相关摘要
    2. 读取摘要内容
    3. 如果有关键词，在原始文件中 grep 细节
    """
    summaries = find_summaries_for_topic(topic)
    if not summaries:
        return f"[未找到主题 '{topic}' 的摘要]\n\n提示: 使用 --list-summaries 查看所有可用摘要"

    output = []
    output.append(f"=" * 60)
    output.append(f"主题: {topic}")
    output.append(f"找到 {len(summaries)} 个相关摘要")
    output.append(f"=" * 60)

    for s in summaries:
        output.append(f"\n### 📄 {s['file']}")
        output.append(f"   创建: {s['created']} | 层级: {s['level']} | 原因: {s['reason']}")
        output.append(f"   原始文件: {', '.join(s['sources'])}")

        # 读取摘要内容
        summary_path = MEMORY_DIR / s["file"]
        if summary_path.exists():
            content = summary_path.read_text(encoding="utf-8", errors="ignore")
            output.append(f"\n{content[:max_lines]}")
            if len(content) > max_lines:
                output.append(f"\n... (内容已截断，原始长度 {len(content)} 字符)")

        # 如果有关键词，在原始文件中 grep
        if keyword:
            hits = grep_original(s["sources"], keyword)
            if hits:
                output.append(f"\n--- grep '{keyword}' 结果 ---")
                for fname, lines in hits.items():
                    output.append(f"\n[{fname}]")
                    for line in lines[:20]:
                        output.append(f"  {line}")
            else:
                output.append(f"\n(grep '{keyword}' 无命中)")

    return "\n".join(output)


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Memory Expand — 上下文还原工具")
    parser.add_argument("--topic", type=str, help="指定要展开的主题")
    parser.add_argument("--query", type=str, help="在原始文件中 grep 的关键词")
    parser.add_argument("--list-summaries", action="store_true", help="列出所有摘要文件")
    parser.add_argument("--trace", type=str, help="追溯指定文件的压缩链")
    parser.add_argument("--max-lines", type=int, default=1000, help="最大输出行数")
    args = parser.parse_args()

    print()

    if args.list_summaries:
        summaries = list_summaries()
        if not summaries:
            print("未找到任何摘要文件")
            return
        print(f"共 {len(summaries)} 个摘要文件:\n")
        print(f"{'文件名':<45} {'主题':<20} {'层级':<10} {'来源数':<6}")
        print("-" * 85)
        for s in summaries:
            sources_count = len(s.get("sources", []))
            print(f"{s['file']:<45} {s['topic']:<20} {s['level']:<10} {sources_count:<6}")

    elif args.trace:
        fpath = MEMORY_DIR / args.trace
        if not fpath.exists():
            fpath = Path(args.trace)
        trace = trace_file(fpath)
        print("=" * 60)
        print(f"文件: {trace['file']}")
        print("=" * 60)
        if "error" in trace:
            print(f"错误: {trace['error']}")
        else:
            if trace.get("merged_into"):
                print(f"\n🔗 被合并进:")
                for target in trace["merged_into"]:
                    print(f"   - {target}")
            if trace.get("sources"):
                print(f"\n📦 原始来源文件:")
                for src in trace["sources"]:
                    print(f"   - {src}")
            if trace.get("topic"):
                print(f"\n📌 主题: {trace['topic']} | 层级: {trace.get('level', 'unknown')}")
            print(f"\n内容预览:\n{trace['content_preview']}")

    elif args.topic:
        result = expand_topic(args.topic, keyword=args.query, max_lines=args.max_lines)
        print(result)

    else:
        print("用法:")
        print("  --list-summaries         列出所有摘要文件")
        print("  --topic <name>            展开某个主题的完整上下文")
        print("  --topic <name> --query K  展开并 grep 关键词 K")
        print("  --trace <file>            追溯指定文件的压缩链")


if __name__ == "__main__":
    main()
