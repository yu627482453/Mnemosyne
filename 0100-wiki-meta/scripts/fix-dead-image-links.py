#!/usr/bin/env python3
"""自动修复图片死链 - M1图片修复工具"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

WIKI_ROOT = Path(__file__).parent.parent.parent
RESOURCE_DIR = WIKI_ROOT / "0001-resource"


def find_image_in_resources(image_slug: str) -> Path | None:
    """在0001-resource/目录下查找图片文件（模糊匹配）"""
    # 精确匹配
    for img_file in RESOURCE_DIR.rglob("*"):
        if img_file.is_file() and img_file.stem == Path(image_slug).stem:
            return img_file

    # 提取核心词（去掉时间戳）进行模糊匹配
    slug_stem = Path(image_slug).stem
    # 去掉时间戳模式（8位或14位数字）
    core_name = re.sub(r'-\d{8,14}$', '', slug_stem)

    for img_file in RESOURCE_DIR.rglob("*"):
        if not img_file.is_file():
            continue
        # 检查核心词是否在实际文件名中
        if core_name in img_file.stem:
            return img_file

    return None


def extract_image_links(md_file: Path) -> List[Tuple[str, int]]:
    """提取文件中所有图片wikilink及其行号"""
    try:
        lines = md_file.read_text(encoding='utf-8').splitlines()
    except Exception:
        return []

    results = []
    for line_num, line in enumerate(lines, start=1):
        matches = re.findall(r'!\[\[([^\]]+)\]\]', line)
        for match in matches:
            results.append((match, line_num))

    return results


def check_image_exists_exact(image_path_or_slug: str) -> bool:
    """检查图片引用是否可以直接解析（不需要修复）"""
    full_path = WIKI_ROOT / image_path_or_slug
    if full_path.exists():
        return True

    # 精确文件名匹配（不使用模糊匹配）
    for img_file in RESOURCE_DIR.rglob("*"):
        if img_file.is_file() and img_file.name == Path(image_path_or_slug).name:
            return True

    return False


def fix_image_link(md_file: Path, dry_run: bool = True) -> int:
    """修复单个文件的图片死链"""
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] 无法读取: {e}")
        return 0

    fixed_count = 0
    lines = content.splitlines()

    for line_num, line in enumerate(lines):
        matches = list(re.finditer(r'!\[\[([^\]]+)\]\]', line))
        if not matches:
            continue

        new_line = line
        for match in matches:
            img_ref = match.group(1)

            if check_image_exists_exact(img_ref):
                continue

            img_slug = Path(img_ref).name
            actual_path = find_image_in_resources(img_slug)

            if actual_path:
                rel_path = actual_path.relative_to(WIKI_ROOT)
                correct_ref = str(rel_path).replace('\\', '/')

                new_line = new_line.replace(
                    f'![[{img_ref}]]',
                    f'![[{correct_ref}]]'
                )
                fixed_count += 1

                rel_md = md_file.relative_to(WIKI_ROOT)
                print(f"  [FIX] {rel_md}:{line_num+1}")
                print(f"    旧: ![[{img_ref}]]")
                print(f"    新: ![[{correct_ref}]]")

        if new_line != line:
            lines[line_num] = new_line

    if fixed_count > 0 and not dry_run:
        try:
            md_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            print(f"  [WRITE] 已写入修复")
        except Exception as e:
            print(f"  [ERROR] 写入失败: {e}")
            return 0

    return fixed_count


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="修复图片死链")
    parser.add_argument('--dry-run', action='store_true',
                       help='仅预览修复，不实际写入')
    parser.add_argument('--file', type=str,
                       help='仅修复指定文件（相对路径）')
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN 模式（预览修复，不写入）===\n")
    else:
        print("=== 执行修复（将写入文件）===\n")

    total_fixed = 0
    total_files = 0

    if args.file:
        target = WIKI_ROOT / args.file
        if not target.exists():
            print(f"[ERROR] 文件不存在: {args.file}")
            return 1
        files_to_check = [target]
    else:
        files_to_check = []
        for pattern in ['0102-wiki-concepts/**/*.md', '3000-*/**/*.md',
                       '3001-*/**/*.md', '3200-*/**/*.md']:
            files_to_check.extend(WIKI_ROOT.glob(pattern))

    for md_file in files_to_check:
        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        if any(p in rel_path for p in ['.trash', '.git', '0000-meta',
                                        '0100-wiki-meta', '0003-inbox', '0109-log']):
            continue

        fixed = fix_image_link(md_file, dry_run=args.dry_run)
        if fixed > 0:
            total_files += 1
            total_fixed += fixed

    print(f"\n=== 汇总 ===")
    print(f"修复文件数: {total_files}")
    print(f"修复死链数: {total_fixed}")

    if args.dry_run and total_fixed > 0:
        print("\n提示：移除 --dry-run 参数以实际写入修复")

    return 0


if __name__ == "__main__":
    sys.exit(main())
