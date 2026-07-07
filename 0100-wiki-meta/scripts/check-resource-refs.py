#!/usr/bin/env python3
"""检查 resource_refs 字段与实际图片引用的一致性"""
import sys
import re
import yaml
from pathlib import Path
from typing import List, Set

WIKI_ROOT = Path(__file__).parent.parent.parent


def extract_image_refs(content: str) -> Set[str]:
    """提取正文中的图片引用 ![[filename]]"""
    pattern = r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|svg|webp))\]\]'
    matches = re.findall(pattern, content, re.IGNORECASE)
    return {m[0] for m in matches}


def check_resource_refs_consistency(md_file: Path) -> List[str]:
    """检查resource_refs与正文图片引用的一致性"""
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

    refs_in_fm = set(fm.get('resource_refs') or [])
    refs_in_content = extract_image_refs(content)

    # 双向检查
    orphaned_fm = refs_in_fm - refs_in_content
    orphaned_content = refs_in_content - refs_in_fm

    if orphaned_fm:
        issues.append(f"resource_refs中有未使用的图片: {', '.join(sorted(orphaned_fm))}")

    if orphaned_content:
        issues.append(f"正文图片未登记到resource_refs: {', '.join(sorted(orphaned_content))}")

    return issues


def main():
    """扫描所有L2/L3文件并检查resource_refs一致性"""
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

        # 执行resource_refs检查
        issues = check_resource_refs_consistency(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现resource_refs一致性问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有resource_refs一致性正常")
        sys.exit(0)


if __name__ == "__main__":
    main()
