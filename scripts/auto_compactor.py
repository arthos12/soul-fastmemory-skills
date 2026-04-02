#!/usr/bin/env python3
"""
auto_compactor.py — fanout-based automatic memory compaction

基于 LCM 思想和 fast-memory compaction_rules.md
执行内存文件的自动压缩、合并、与溯源链生成

使用方式:
  python scripts/auto_compactor.py                    # 全量检查
  python scripts/auto_compactor.py --check-only       # 仅检查不执行
  python scripts/auto_compactor.py --topic <name>     # 指定主题压缩
  python scripts/auto_compactor.py --dry-run           # 模拟执行
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import re

# 配置路径
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
SKILL_REFS = WORKSPACE / "skills" / "fast-memory" / "references"
COMPACTION_LOG = ARCHIVE_DIR / "compaction_log.md"

# === 默认参数（可被规则文件覆盖）===
DEFAULTS = {
    "MAX_DAILY_LINES": 200,
    "MIN_FANOUT_LEAF": 3,
    "MIN_FANOUT_ROOT": 3,
    "MAX_FANOUT": 20,
    "COMPACTION_INTERVAL_H": 24,
    "MAX_COMPACTION_PER_SESSION": 2,
    "ARCHIVE_RETENTION_DAYS": 7,
    "SUMMARY_TARGET_LINES": (50, 150),
    "ROOT_SUMMARY_TARGET_LINES": (100, 300),
}

# ============================================================================
# 核心数据结构
# ============================================================================

class CompactionCandidate:
    """压缩候选对象"""
    def __init__(self, file_path: Path, reason: str, size_mb: float = 0):
        self.file_path = file_path
        self.reason = reason  # "size_overflow" | "fanout_ge_5" | "manual"
        self.size_mb = size_mb
        self.lines = 0
        self.topics: Set[str] = set()
        self.last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        self.last_compacted: Optional[datetime] = None
        self.can_compact = False
        self.can_delete_after = False


# ============================================================================
# 工具函数
# ============================================================================

def ensure_archive_dir():
    """确保 archive 目录存在"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def load_compaction_log() -> Dict[str, datetime]:
    """加载已完成的压缩记录，避免频繁重压缩"""
    last_compact = {}
    if not COMPACTION_LOG.exists():
        return last_compact
    content = COMPACTION_LOG.read_text()
    # 解析: ## <timestamp> deleted: <file>
    for line in content.split("\n"):
        if "deleted:" in line and "merged_into:" in line:
            m = re.search(r"deleted:\s*(.+?)\s*$", line)
            t = re.search(r"## (.+?) ", line)
            if m and t:
                last_compact[m.group(1).strip()] = datetime.fromisoformat(t.group(1))
    return last_compact


def get_topic_from_filename(filename: str) -> str:
    """从文件名提取主题标签"""
    # memory/2026-03-21_soul-upgrade_discussion.md
    # → soul-upgrade_discussion
    name = Path(filename).stem  # 去掉 .md
    # 去掉日期前缀
    if re.match(r"\d{4}-\d{2}-\d{2}_", name):
        name = name[11:]
    return name


def parse_daily_note_topics(file_path: Path) -> Set[str]:
    """从 daily note 内容中提取主题关键词"""
    topics = set()
    name = file_path.stem
    # 文件名本身就含主题
    if "_" in name:
        topics.add(name.split("_", 1)[1])
    # 从内容提取 # 标签
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        hashtags = re.findall(r"#(\w+)", content)
        topics.update(hashtags[:10])  # 最多取10个
    except:
        pass
    return topics


def read_compaction_rules() -> Dict:
    """读取规则文件（如果存在），否则用 DEFAULTS"""
    rules_path = SKILL_REFS / "compaction_rules.md"
    if not rules_path.exists():
        return DEFAULTS.copy()
    # 简单解析：提取 ## 七、配置参数表格中的值
    rules = DEFAULTS.copy()
    try:
        content = rules_path.read_text()
        for key, default in DEFAULTS.items():
            pattern = rf"`{key}`\s*\|\s*.*?\s*\|\s*(.+?)(?:\n|$)"
            m = re.search(pattern, content)
            if m:
                val = m.group(1).strip()
                if isinstance(default, tuple):
                    # 范围值
                    if "-" in val:
                        parts = val.replace("–", "-").split("-")
                        rules[key] = (int(parts[0]), int(parts[1]))
                elif isinstance(default, int):
                    rules[key] = int(val)
    except:
        pass
    return rules


# ============================================================================
# 扫描函数
# ============================================================================

def scan_daily_notes(rules: Dict) -> List[CompactionCandidate]:
    """扫描所有 daily notes，找出超过行数阈值的文件"""
    candidates = []
    if not MEMORY_DIR.exists():
        return candidates

    for f in MEMORY_DIR.glob("????-??-??*.md"):
        if f.name == "compaction_log.md":
            continue
        try:
            lines = sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))
            if lines > rules["MAX_DAILY_LINES"]:
                cand = CompactionCandidate(f, "size_overflow")
                cand.lines = lines
                cand.topics = parse_daily_note_topics(f)
                cand.can_compact = True
                candidates.append(cand)
        except:
            pass
    return candidates


def scan_topic_fanout(rules: Dict) -> Dict[str, List[Path]]:
    """扫描同主题文件 fanout，返回需要压缩的主题"""
    topic_files: Dict[str, List[Path]] = defaultdict(list)
    if not MEMORY_DIR.exists():
        return {}

    for f in MEMORY_DIR.glob("????-??-??*.md"):
        if f.name == "compaction_log.md":
            continue
        topic = get_topic_from_filename(f.name)
        if topic:
            topic_files[topic].append(f)

    # 过滤出 fanout >= MIN_FANOUT_LEAF 的主题
    actionable = {}
    for topic, files in topic_files.items():
        if len(files) >= rules["MIN_FANOUT_LEAF"]:
            actionable[topic] = files
    return actionable


def scan_memory_md(rules: Dict) -> bool:
    """检查 MEMORY.md 是否超过行数阈值"""
    memory_md = WORKSPACE / "MEMORY.md"
    if not memory_md.exists():
        return False
    lines = sum(1 for _ in open(memory_md, encoding="utf-8", errors="ignore"))
    return lines > 500


# ============================================================================
# 核心压缩逻辑
# ============================================================================

def generate_condensed_summary(files: List[Path], topic: str, rules: Dict) -> Tuple[str, List[str]]:
    """
    生成 leaf→condensed 摘要
    返回 (summary_content, source_filenames)
    """
    sources = [f.name for f in files]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 收集所有文件的标题/关键结论
    sections = []
    all_content = []
    for f in sorted(files):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            all_content.append(content)
            # 提取标题行（以 ## 或 # 开头的行）
            headers = re.findall(r"^(#{1,3})\s+(.+)$", content, re.MULTILINE)
            for h in headers[:5]:  # 最多取5个标题
                level, title = h
                sections.append(f"##{level} {title}")  # 保留层级
        except:
            pass

    # 生成摘要内容
    target_min, target_max = rules["SUMMARY_TARGET_LINES"]
    summary_lines = [
        f"# SUMMARY: {topic}",
        f"# created: {timestamp}",
        f"# level: condensed",
        f"# sources: {', '.join(sources)}",
        f"# merged_at: {timestamp}",
        f"# reason: fanout={len(files)}",
        "",
        "## 原始记录摘要",
        "",
    ]

    # 添加各文件的第一个 ## 标题和主要内容行
    for i, (f, content) in enumerate(zip(files, all_content)):
        summary_lines.append(f"### [{f.name}]")
        # 取内容前 30 行作为原始摘要
        content_lines = content.split("\n")[:30]
        for line in content_lines:
            if line.strip() and not line.startswith("#"):
                summary_lines.append(line)
        summary_lines.append("")

    # 关键提炼（从所有内容中提取决策/结论）
    decisions = extract_decisions(all_content)
    if decisions:
        summary_lines.extend([
            "## 关键提炼",
            "",
        ])
        for d in decisions[:10]:  # 最多10条
            summary_lines.append(f"- {d}")
        summary_lines.append("")

    # 未合并细节（保留 grep 路径）
    summary_lines.extend([
        "## 未合并细节（保留原始引用路径）",
        "如需查看完整原始上下文，使用以下 grep 指令：",
        ""
    ])
    for f in files:
        summary_lines.append(f"  grep \"<关键词>\" {f.name}")
    summary_lines.append("")

    content = "\n".join(summary_lines)
    # 如果超长，截断到 target_max
    lines = content.split("\n")
    if len(lines) > target_max:
        content = "\n".join(lines[:target_max]) + f"\n\n<!-- truncated at line {target_max} -->"
    return content, sources


def extract_decisions(contents: List[str]) -> List[str]:
    """从内容中提取决策/结论类语句"""
    decisions = []
    keywords = [
        "确认", "决定", "结论", "采用", "选择", "执行", "开始",
        "同意", "通过", "完了", "完成", "更新", "修改",
        "created", "updated", "decided", "confirmed", "done"
    ]
    for content in contents:
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 跳过超长行
            if len(line) > 300:
                continue
            # 命中关键词
            if any(kw in line for kw in keywords):
                decisions.append(line[:200])
    return decisions


def add_merged_backlink(file_path: Path, summary_name: str, reason: str):
    """为被合并的原始文件追加尾注"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    backlink = (
        f"\n\n---\n"
        f"<!-- 🔗 merged_into: {summary_name} -->\n"
        f"<!-- merged_at: {timestamp} -->\n"
        f"<!-- reason: {reason} -->\n"
        f"<!-- to_restore: grep \"<关键词>\" {summary_name} -->\n"
    )
    try:
        existing = file_path.read_text(encoding="utf-8", errors="ignore")
        # 避免重复追加
        if f"merged_into: {summary_name}" not in existing:
            file_path.write_text(existing + backlink, encoding="utf-8")
    except:
        pass


def archive_file(file_path: Path) -> Path:
    """将文件备份到 archive 目录"""
    ensure_archive_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_bak_{timestamp}.md"
    backup_path = ARCHIVE_DIR / backup_name
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except:
        return file_path  # fallback


def log_compaction(deleted_file: str, merged_into: str, reason: str, backup_path: Path):
    """记录压缩操作到 compaction_log.md"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ensure_archive_dir()
    entry = (
        f"## {timestamp}\n"
        f"- deleted: {deleted_file}\n"
        f"- merged_into: {merged_into}\n"
        f"- reason: {reason}\n"
        f"- backup: {backup_path}\n\n"
    )
    if COMPACTION_LOG.exists():
        existing = COMPACTION_LOG.read_text()
        COMPACTION_LOG.write_text(existing + entry)
    else:
        COMPACTION_LOG.write_text("# Compaction Log\n\n" + entry)


# ============================================================================
# 主流程
# ============================================================================

def run_compaction(check_only: bool = False, dry_run: bool = False,
                   target_topic: Optional[str] = None, max_per_session: int = 2):
    """执行压缩流程"""
    rules = read_compaction_rules()
    session_compaction_count = 0

    print(f"\n{'='*60}")
    print(f"Auto Compactor — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    # 1. 检查 daily notes 超长文件
    print("\n【1/3】检查 daily notes 超长文件...")
    candidates = scan_daily_notes(rules)
    if candidates:
        print(f"  发现 {len(candidates)} 个超长文件:")
        for c in candidates:
            print(f"    - {c.file_path.name}: {c.lines} 行")
    else:
        print("  ✅ 无超长文件")

    # 2. 检查主题 fanout
    print("\n【2/3】检查主题 fanout...")
    topic_fanout = scan_topic_fanout(rules)
    if topic_fanout:
        print(f"  发现 {len(topic_fanout)} 个主题需要合并:")
        for topic, files in topic_fanout.items():
            print(f"    - {topic}: {len(files)} 个文件")
    else:
        print("  ✅ 无需合并的主题")

    # 3. 检查 MEMORY.md
    print("\n【3/3】检查 MEMORY.md...")
    if scan_memory_md(rules):
        print("  ⚠️ MEMORY.md 超过 500 行，需要精简（待单独处理）")
    else:
        print("  ✅ MEMORY.md 正常")

    # === 执行压缩 ===
    if check_only:
        print("\n[check-only 模式，仅检查不执行]")
        return

    if dry_run:
        print("\n[dry-run 模式，仅报告不执行]")
        return

    # 压缩主题 fanout（最优先）
    if target_topic:
        if target_topic in topic_fanout and session_compaction_count < max_per_session:
            files = topic_fanout[target_topic]
            print(f"\n>>> 压缩主题: {target_topic} ({len(files)} 个文件)")
            summary_content, sources = generate_condensed_summary(files, target_topic, rules)
            summary_name = f"{datetime.now().strftime('%Y-%m-%d')}_{target_topic}_summary.md"
            summary_path = MEMORY_DIR / summary_name
            summary_path.write_text(summary_content, encoding="utf-8")
            print(f"    生成: {summary_name}")
            # 追加尾注到原文件
            for f in files:
                add_merged_backlink(f, summary_name, f"fanout={len(files)}")
            session_compaction_count += 1
    else:
        for topic, files in topic_fanout.items():
            if session_compaction_count >= max_per_session:
                print(f"\n⚠️ 达到单 session 上限 ({max_per_session})，暂停")
                break
            if topic == target_topic or target_topic is None:
                print(f"\n>>> 压缩主题: {topic} ({len(files)} 个文件)")
                summary_content, sources = generate_condensed_summary(files, topic, rules)
                summary_name = f"{datetime.now().strftime('%Y-%m-%d')}_{topic}_summary.md"
                summary_path = MEMORY_DIR / summary_name
                summary_path.write_text(summary_content, encoding="utf-8")
                print(f"    生成: {summary_name}")
                for f in files:
                    add_merged_backlink(f, summary_name, f"fanout={len(files)}")
                session_compaction_count += 1

    print(f"\n{'='*60}")
    print(f"完成。压缩了 {session_compaction_count} 个主题")
    print(f"{'='*60}")


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Fast Memory Auto Compactor")
    parser.add_argument("--check-only", action="store_true", help="仅检查不执行")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    parser.add_argument("--topic", type=str, help="指定压缩某个主题")
    parser.add_argument("--max-per-session", type=int, default=2, help="单 session 最大压缩次数")
    args = parser.parse_args()

    run_compaction(
        check_only=args.check_only,
        dry_run=args.dry_run,
        target_topic=args.topic,
        max_per_session=args.max_per_session
    )


if __name__ == "__main__":
    main()
