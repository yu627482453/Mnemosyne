#!/usr/bin/env python3
"""批量操作CLI - 支持tags/status/trash批量处理"""
import sys
import re
import shutil
from pathlib import Path
from typing import List
import yaml

WIKI_ROOT = Path(__file__).parent.parent.parent
TRASH_DIR = WIKI_ROOT / ".trash"


def parse_frontmatter(md_file: Path) -> tuple[dict, str]:
    """解析frontmatter和正文"""
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception:
        return {}, content

    if not content.startswith('---'):
        return {}, content

    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    try:
        fm = yaml.safe_load(match.group(1)) or {}
        body = match.group(2)
        return fm, body
    except Exception:
        return {}, content


def write_frontmatter(md_file: Path, fm: dict, body: str):
    """写回frontmatter和正文"""
    fm_text = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    content = f"---\n{fm_text}---\n{body}"
    md_file.write_text(content, encoding='utf-8')


def batch_add_tags(files: List[Path], tags: List[str], dry_run: bool = True):
    """批量添加tags"""
    count = 0
    for md_file in files:
        fm, body = parse_frontmatter(md_file)
        if not fm:
            continue

        existing_tags = fm.get('tags', [])
        if not isinstance(existing_tags, list):
            existing_tags = [existing_tags]

        new_tags = existing_tags + [t for t in tags if t not in existing_tags]

        if len(new_tags) != len(existing_tags):
            fm['tags'] = new_tags
            if not dry_run:
                write_frontmatter(md_file, fm, body)
            count += 1
            rel_path = md_file.relative_to(WIKI_ROOT)
            print(f"  [ADD] {rel_path}: +{len(new_tags) - len(existing_tags)} tags")

    return count


def batch_set_status(files: List[Path], status: str, dry_run: bool = True):
    """批量设置status"""
    count = 0
    for md_file in files:
        fm, body = parse_frontmatter(md_file)
        if not fm:
            continue

        if fm.get('status') != status:
            fm['status'] = status
            if not dry_run:
                write_frontmatter(md_file, fm, body)
            count += 1
            rel_path = md_file.relative_to(WIKI_ROOT)
            print(f"  [SET] {rel_path}: status={status}")

    return count


def batch_move_trash(files: List[Path], dry_run: bool = True):
    """批量移动到.trash/"""
    TRASH_DIR.mkdir(exist_ok=True)
    count = 0

    for md_file in files:
        rel_path = md_file.relative_to(WIKI_ROOT)
        trash_path = TRASH_DIR / rel_path
        trash_path.parent.mkdir(parents=True, exist_ok=True)

        if not dry_run:
            shutil.move(str(md_file), str(trash_path))
        count += 1
        print(f"  [TRASH] {rel_path} → .trash/")

    return count


def main():
    """CLI主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="批量操作CLI")
    parser.add_argument('operation', choices=['add-tags', 'set-status', 'move-trash'],
                       help='操作类型')
    parser.add_argument('--pattern', type=str, required=True,
                       help='文件匹配模式（如 "3000-*/*.md"）')
    parser.add_argument('--tags', type=str,
                       help='要添加的tags（逗号分隔）')
    parser.add_argument('--status', type=str,
                       help='要设置的status（draft/published）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际修改')
    args = parser.parse_args()

    files = list(WIKI_ROOT.glob(args.pattern))
    files = [f for f in files if f.is_file() and f.suffix == '.md']

    if not files:
        print(f"未找到匹配的文件：{args.pattern}")
        return 1

    print(f"找到 {len(files)} 个文件")
    if args.dry_run:
        print("[DRY RUN 模式]")

    count = 0
    if args.operation == 'add-tags':
        if not args.tags:
            print("错误：--tags 参数必需")
            return 1
        tags = [t.strip() for t in args.tags.split(',')]
        count = batch_add_tags(files, tags, args.dry_run)
    elif args.operation == 'set-status':
        if not args.status:
            print("错误：--status 参数必需")
            return 1
        count = batch_set_status(files, args.status, args.dry_run)
    elif args.operation == 'move-trash':
        count = batch_move_trash(files, args.dry_run)

    print(f"\n完成：{count} 个文件被处理")
    if args.dry_run:
        print("提示：移除 --dry-run 以实际执行")

    return 0


if __name__ == "__main__":
    sys.exit(main())
