#!/usr/bin/env python3
"""检查正文中是否残留远程图片链接"""
import sys
import re
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent

REMOTE_IMAGE_PATTERN = r'!\[.*?\]\((https?://[^\)]+)\)'


def check_remote_images(md_file: Path) -> List[str]:
    """返回远程图片URL列表"""
    issues = []

    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        return [f"无法读取文件: {e}"]

    matches = re.findall(REMOTE_IMAGE_PATTERN, content)
    if matches:
        for url in matches:
            issues.append(f"残留远程图片: {url}")

    return issues


def main():
    """扫描所有L2/L3文件并检查远程图片残留"""
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

            import yaml
            fm = yaml.safe_load(m.group(1)) or {}
            layer = fm.get('layer', '')
            if layer not in ('L2', 'L3'):
                continue
        except Exception:
            continue

        # 执行远程图片检查
        issues = check_remote_images(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现远程图片残留（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 无远程图片残留")
        sys.exit(0)


if __name__ == "__main__":
    main()
