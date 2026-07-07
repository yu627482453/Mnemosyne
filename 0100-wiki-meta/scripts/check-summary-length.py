#!/usr/bin/env python3
"""检查 summary 字段长度"""
import sys
import re
import yaml
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent

MIN_SUMMARY_LENGTH = 200


def check_summary_length(md_file: Path) -> List[str]:
    """检查summary字段长度"""
    issues = []

    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        return [f"无法读取文件: {e}"]

    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        return [f"frontmatter解析失败: {e}"]

    summary = fm.get('summary', '')

    if not summary:
        issues.append("缺少summary字段")
    elif len(summary) < MIN_SUMMARY_LENGTH:
        issues.append(f"summary过短（{len(summary)}/{MIN_SUMMARY_LENGTH}字符）")

    return issues


def main():
    """扫描所有L2/L3文件并检查summary长度"""
    has_issues = False

    for md_file in WIKI_ROOT.rglob("*.md"):
        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        # 跳过非内容目录
        if any(p in rel_path for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta',
                                         '0003-inbox', '0109-log']):
            continue

        # 检查是否是L2/L3文件
        try:
            text = md_file.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not m:
                continue

            fm = yaml.safe_load(m.group(1)) or {}
            layer = fm.get('layer', '')
            if layer not in ('L2', 'L3'):
                continue
        except Exception:
            continue

        # 执行summary长度检查
        issues = check_summary_length(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现summary长度问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有summary长度符合要求")
        sys.exit(0)


if __name__ == "__main__":
    main()
