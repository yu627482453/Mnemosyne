#!/usr/bin/env python3
"""检查 tags 字段格式规范"""
import sys
import re
import yaml
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent

TAG_PATTERN = r'^[a-z0-9]+(-[a-z0-9]+)*$'  # kebab-case


def check_tags_format(md_file: Path) -> List[str]:
    """检查tags格式规范"""
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

    tags = fm.get('tags') or []

    # 检查数量
    if len(tags) < 5:
        issues.append(f"tags数量不足（{len(tags)}/5）")
    elif len(tags) > 10:
        issues.append(f"tags数量过多（{len(tags)}/10）")

    # 检查格式
    for tag in tags:
        if not isinstance(tag, str):
            continue

        if ' ' in tag:
            issues.append(f"tag含空格: '{tag}'")
        elif not re.match(TAG_PATTERN, tag):
            issues.append(f"tag格式不符（应kebab-case）: '{tag}'")

    return issues


def main():
    """扫描所有L2/L3文件并检查tags格式"""
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

        # 执行tags格式检查
        issues = check_tags_format(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现tags格式问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有tags格式规范")
        sys.exit(0)


if __name__ == "__main__":
    main()
