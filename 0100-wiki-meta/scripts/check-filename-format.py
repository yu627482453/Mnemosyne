#!/usr/bin/env python3
"""检查文件名格式规范"""
import sys
import re
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent

INVALID_CHARS = r'[/:*?"<>|+#\s]'  # 空格+特殊字符
MULTIPLE_DOTS = r'\..*\.'  # 多个点（扩展名前）


def check_filename(path: Path) -> List[str]:
    """返回文件名问题列表"""
    issues = []
    name = path.stem  # 不含扩展名

    # 检查非法字符
    if re.search(INVALID_CHARS, name):
        issues.append(f"文件名包含非法字符或空格: {name}")

    # 检查多个点
    if re.search(MULTIPLE_DOTS, name):
        issues.append(f"文件名扩展名前有多余的点: {name}")

    # 检查大小写（应全小写）
    if name != name.lower():
        issues.append(f"文件名应全小写: {name} -> {name.lower()}")

    # 检查连续符号
    if '--' in name or '__' in name:
        issues.append(f"文件名有连续符号: {name}")

    return issues


def main():
    """扫描所有L2/L3文件并检查文件名格式"""
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

        # 执行文件名检查
        issues = check_filename(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现文件名格式问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有文件名格式规范")
        sys.exit(0)


if __name__ == "__main__":
    main()
