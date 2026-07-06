#!/usr/bin/env python3
"""
update-hot.py - 更新 hot.md 热缓存（简化版）

用途：Ingest/Update 后更新热缓存

使用：
  python update-hot.py add-l2 "3000-Agent/file.md"
  python update-hot.py add-l3 "0102-wiki-concepts/agent/loop.md"
"""

import sys
import re
import yaml
from datetime import datetime
from pathlib import Path

HOT_FILE = Path(__file__).parent.parent / "hot.md"
WIKI_ROOT = Path(__file__).parent.parent.parent
MAX_ENTRIES_PER_SECTION = 20  # 每区域最多保留条目数

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def extract_title(file_path: str) -> str:
    """从 frontmatter 提取真实 title，路径转换作降级兜底"""
    full_path = WIKI_ROOT / file_path
    if full_path.exists():
        try:
            text = full_path.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1)) or
                if fm.get('title'):
                    return str(fm['title'])
        except Exception:
            pass
    # 降级兜底：从路径解析
    return Path(file_path).stem.replace('-', ' ').title()

def trim_section(lines: list, section_prefix: str) -> list:
    """限制区域内条目数，保留最新 MAX_ENTRIES_PER_SECTION 条"""
    result, entries, in_section = [], [], False
    for line in lines:
        if line.startswith(section_prefix):
            in_section = True
            result.append(line)
        elif in_section and (line.startswith('###') or line.startswith('##')):
            # 只保留最新的条目
            result.extend(entries[-MAX_ENTRIES_PER_SECTION:])
            result.append(line)
            in_section = False
            entries = []
        elif in_section and line.startswith('- '):
            entries.append(line)
        else:
            result.append(line)
    # 处理文件末尾的区域
    if in_section:
        result.extend(entries[-MAX_ENTRIES_PER_SECTION:])
    return result

def add_l2(file_path):
    """添加新建的 L2 到 hot.md"""
    if not HOT_FILE.exists():
        print(f"错误: {HOT_FILE} 不存在", file=sys.stderr)
        return 1

    content = HOT_FILE.read_text(encoding='utf-8')
    title = extract_title(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d")

    # 查找 "### 新建 L2" 区域并插入
    new_entry = f"- [[{title}]] ({timestamp})"

    lines = content.split('\n')
    new_lines = []
    in_l2_section = False
    inserted = False

    for line in lines:
        if line.startswith('### 新建 L2'):
            in_l2_section = True
            new_lines.append(line)
        elif in_l2_section and not inserted and (line.startswith('###') or line.startswith('##')):
            # 在下一个区域前插入
            new_lines.append(new_entry)
            new_lines.append(line)
            inserted = True
        else:
            new_lines.append(line)

    # 应用条目上限
    new_lines = trim_section(new_lines, '### 新建 L2')

    # 更新 updated 时间戳
    for i, line in enumerate(new_lines):
        if line.startswith('updated:'):
            new_lines[i] = f"updated: {get_timestamp()}"
            break

    HOT_FILE.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ 已添加 L2: {title}")
    return 0

def add_l3(file_path):
    """添加新建的 L3 到 hot.md"""
    # 与 add_l2 类似逻辑，定位到 "### 新建 L3" 区域
    content = HOT_FILE.read_text(encoding='utf-8')
    title = extract_title(file_path)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"- [[{title}]] ({timestamp})"

    lines = content.split('\n')
    new_lines = []
    found_section = False

    for line in lines:
        new_lines.append(line)
        if line.startswith('### 新建 L3') and not found_section:
            found_section = True
            new_lines.append(new_entry)

    # 应用条目上限
    new_lines = trim_section(new_lines, '### 新建 L3')

    # 更新时间戳
    for i, line in enumerate(new_lines):
        if line.startswith('updated:'):
            new_lines[i] = f"updated: {get_timestamp()}"
            break

    HOT_FILE.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ 已添加 L3: {title}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python update-hot.py <add-l2|add-l3> <文件路径>")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if action == "add-l2":
        sys.exit(add_l2(file_path))
    elif action == "add-l3":
        sys.exit(add_l3(file_path))
    else:
        print(f"未知操作: {action}")
        sys.exit(1)
