#!/usr/bin/env python3
"""检查 L2 文件结构完整性"""
import sys
import re
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent

def check_l2_structure(md_file: Path) -> List[str]:
    """返回问题列表，空列表表示通过"""
    issues = []

    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        return [f"无法读取文件: {e}"]

    # 移除frontmatter
    content_without_fm = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # 检查是否有分隔线
    if '\n---\n' not in content_without_fm:
        issues.append("缺少核心提炼区与原文笔记区的分隔线（---）")
        return issues

    upper, lower = content_without_fm.split('\n---\n', 1)

    # 检查核心提炼区关键元素
    required_sections = ['核心提炼', '关键概念', '原文要点', '来源']
    for section in required_sections:
        if section not in upper:
            issues.append(f"核心提炼区缺少「{section}」段落")

    # 检查原文笔记区是否为空
    if len(lower.strip()) < 100:
        issues.append("原文笔记区内容过少（<100字符）")

    return issues


def main():
    """扫描所有L2文件并检查结构"""
    has_issues = False

    for md_file in WIKI_ROOT.rglob("*.md"):
        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        # 跳过非L2目录
        if any(p in rel_path for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta',
                                         '0003-inbox', '0101-wiki-topics', '0102-wiki-concepts',
                                         '0103-wiki-entities', '0104-wiki-comparisons',
                                         '0105-wiki-base', '0109-log']):
            continue

        # 检查是否是L2文件
        try:
            text = md_file.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not m:
                continue

            import yaml
            fm = yaml.safe_load(m.group(1)) or {}
            if fm.get('layer') != 'L2':
                continue
        except Exception:
            continue

        # 执行结构检查
        issues = check_l2_structure(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现L2结构问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有L2文件结构完整")
        sys.exit(0)


if __name__ == "__main__":
    main()
