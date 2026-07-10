#!/usr/bin/env python3
"""L3 文件目录重定位工具 — 移动文件、更新引用、同步索引"""
import sys, os, re, yaml, sqlite3, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent

def load_frontmatter(file_path):
    """读取 Markdown 文件的 frontmatter"""
    try:
        text = file_path.read_text(encoding='utf-8')
        m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
        if not m:
            return None, text
        fm = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
        return fm, body
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None, None

def save_file(file_path, frontmatter, body):
    """保存 Markdown 文件（frontmatter + body）"""
    try:
        fm_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        content = f"---\n{fm_text}---{body}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False

def update_references(old_path, new_path):
    """更新所有引用该文件的 wikilink"""
    old_slug = old_path.stem
    new_slug = new_path.stem

    # 如果 slug 没变，只有路径变了，wikilink 不需要更新
    if old_slug == new_slug:
        print(f"✓ Slug 未变化，wikilink 无需更新")
        return True

    # 搜索所有 MD 文件中的 wikilink
    updated_count = 0
    for md in ROOT.rglob("*.md"):
        if '.trash' in str(md) or '.git' in str(md):
            continue

        try:
            content = md.read_text(encoding='utf-8')
            pattern = rf'\[\[{old_slug}(\|[^\]]+)?\]\]'
            if re.search(pattern, content):
                new_content = re.sub(pattern, rf'[[{new_slug}\1]]', content)
                md.write_text(new_content, encoding='utf-8')
                updated_count += 1
        except Exception:
            continue

    print(f"✓ 更新了 {updated_count} 个文件的 wikilink 引用")
    return True

def log_relocation(old_path, new_path, reason):
    """记录重定位操作到日志文件"""
    log_dir = ROOT / "0109-log"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = log_dir / f"relocate-{timestamp}.md"

    log_content = f"""---
operation: relocate
timestamp: {datetime.now().isoformat()}
---

# L3 重定位操作

- **原路径**: {old_path}
- **新路径**: {new_path}
- **理由**: {reason}
- **状态**: 完成
"""

    try:
        log_file.write_text(log_content, encoding='utf-8')
        print(f"✓ 日志已记录到: {log_file.relative_to(ROOT)}")
        return True
    except Exception as e:
        print(f"⚠️  日志记录失败: {e}")
        return False

def relocate_l3(old_path_str, new_path_str, reason="用户确认"):
    """执行 L3 文件重定位"""
    old_path = ROOT / old_path_str
    new_path = ROOT / new_path_str

    print(f"\n📦 开始重定位 L3 文件...")
    print(f"  原路径: {old_path_str}")
    print(f"  新路径: {new_path_str}")

    # 1. 验证原文件存在
    if not old_path.exists():
        print(f"❌ 原文件不存在: {old_path}")
        return False

    # 2. 检查目标位置是否已有文件
    if new_path.exists():
        print(f"⚠️  目标位置已存在文件，需手动处理合并")
        return False

    # 3. 读取 frontmatter
    fm, body = load_frontmatter(old_path)
    if fm is None:
        return False

    # 4. 更新 frontmatter 的 updated 字段
    fm['updated'] = datetime.now().strftime("%Y-%m-%d")

    # 5. 创建目标目录并移动文件
    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if not save_file(new_path, fm, body):
            return False
        print(f"✓ 文件已写入新位置")
    except Exception as e:
        print(f"❌ 移动文件失败: {e}")
        return False

    # 6. 删除原文件
    try:
        old_path.unlink()
        print(f"✓ 原文件已删除")
    except Exception as e:
        print(f"❌ 删除原文件失败: {e}")
        return False

    # 7. 更新引用
    update_references(old_path, new_path)

    # 8. 记录日志
    log_relocation(old_path_str, new_path_str, reason)

    print(f"\n✅ 重定位完成！")
    print(f"\n⚠️  后续操作：")
    print(f"  1. 运行 index-notes.py 更新索引")
    print(f"  2. 运行 check-config-sync.py 验证配置")
    print(f"  3. 执行 git add/commit")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python relocate-l3.py <原路径> <新路径> [理由]")
        print("示例: python relocate-l3.py '0102-wiki-concepts/agent/core/agent-loop.md' '0102-wiki-concepts/agent/loop/agent-loop.md' '更适合loop子分类'")
        sys.exit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]
    reason = sys.argv[3] if len(sys.argv) > 3 else "用户确认"

    success = relocate_l3(old_path, new_path, reason)
    sys.exit(0 if success else 1)
