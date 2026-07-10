#!/usr/bin/env python3
"""检查 ingest 后配置同步是否完整 — 退出码非 0 则阻断 commit"""
import sys, os, re, json, sqlite3, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
errors = []

def err(rule: str, msg: str):
    errors.append(f"FAIL [{rule}] {msg}")

def load_all_frontmatter():
    """收集所有 L2/L3 文件的 frontmatter"""
    notes = []
    for md in ROOT.rglob("*.md"):
        rel = str(md.relative_to(ROOT)).replace('\\', '/')
        if any(p in rel for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta', '0003-inbox', '0109-log']):
            continue
        try:
            text = md.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            layer = fm.get('layer', '')
            if layer in ('L2', 'L3'):
                fm['_path'] = rel
                notes.append(fm)
        except Exception:
            continue
    return notes

# === 8a: topics.yaml active ===
topics_file = ROOT / "0100-wiki-meta" / "configs" / "topics.yaml"
try:
    topics_cfg = yaml.safe_load(topics_file.read_text(encoding='utf-8'))
except Exception as e:
    err("topics_active", f"无法读取 topics.yaml: {e}")
    topics_cfg = None

active_topics = set()
if topics_cfg:
    for domain_name, domain_data in (topics_cfg.get('domains') or {}).items():
        for t in (domain_data.get('active') or []):
            active_topics.add(t)

notes = load_all_frontmatter()

# 收集所有 L2 用到的 topic
l2_topics = set()
for n in notes:
    if n.get('layer') == 'L2' and n.get('topic'):
        l2_topics.add(n['topic'])

for t in l2_topics:
    if t not in active_topics:
        err("topic_not_in_active", f"L2 topic '{t}' 未注册到 topics.yaml active 列表")

# === 8b: tag-vocabulary ===
tag_file = ROOT / "0100-wiki-meta" / "configs" / "tag-vocabulary.yaml"
try:
    tag_cfg = yaml.safe_load(tag_file.read_text(encoding='utf-8'))
    raw = tag_cfg.get('vocabulary') or []
    registered_tags = {e.get('tag_en') if isinstance(e, dict) else e for e in raw}
except Exception:
    registered_tags = set()

for n in notes:
    for tag in (n.get('tags') or []):
        if isinstance(tag, str) and tag not in registered_tags:
            err("tag_not_in_vocabulary", f"{n.get('_path', '?')} 使用了未登记标签: {tag}")

# === 8c: 0101-wiki-topics 综述页 ===
topic_pages_dir = ROOT / "0101-wiki-topics"
existing_topic_pages = set()
if topic_pages_dir.exists():
    for f in topic_pages_dir.rglob("*.md"):
        try:
            text = f.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                topic = fm.get('topic', '')
                if topic:
                    existing_topic_pages.add(topic)
        except Exception:
            continue

for t in active_topics:
    if t not in existing_topic_pages:
        err("topic_missing_summary_page", f"active topic '{t}' 缺少 0101-wiki-topics 域级综述页")

# === 8d: .wiki.db 覆盖 ===
db_path = ROOT / ".wiki.db"
if db_path.exists():
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        cur = conn.cursor()
        cur.execute("SELECT path FROM notes")
        indexed_paths = {row[0] for row in cur.fetchall()}
        conn.close()

        # 正向检查：文件是否在 DB 中
        for n in notes:
            p = n.get('_path', '')
            if p and p not in indexed_paths:
                err("not_indexed", f"{p} 未同步到 .wiki.db")

        # 反向检查：DB 中是否有已删除文件的过期条目
        file_paths = {n.get('_path') for n in notes}
        for indexed_path in indexed_paths:
            if indexed_path not in file_paths:
                err("stale_index",
                    f"DB 中存在过期条目：{indexed_path}（文件已删除，请重新运行 index-notes.py）")
    except Exception as e:
        err("wiki_db", f"无法读取 .wiki.db: {e}")
else:
    err("wiki_db", ".wiki.db 不存在")

# === 8e: planned_links 残留 ===
for n in notes:
    if n.get('layer') == 'L2':
        planned = n.get('planned_links') or []
        for target in planned:
            if not isinstance(target, str):
                continue
            # 检查是否有对应文件存在
            found = False
            for md in ROOT.rglob(f"{target}.md"):
                rel = str(md.relative_to(ROOT))
                if '.trash' not in rel and '.git' not in rel:
                    found = True
                    break
            if found:
                err("stale_planned_link", f"{n.get('_path', '?')} planned_links 中 '{target}' 已存在，应清理")

# === 8h: L3 目录对齐检查 ===
inference_file = ROOT / "0100-wiki-meta" / "configs" / "l3-directory-inference.yaml"
if inference_file.exists():
    try:
        inference_cfg = yaml.safe_load(inference_file.read_text(encoding='utf-8'))
        tag_patterns = inference_cfg.get('tag_patterns', [])
        fallback_map = inference_cfg.get('fallback', {})

        for n in notes:
            if n.get('layer') != 'L3':
                continue

            path = n.get('_path', '')
            if not path:
                continue

            # 提取物理目录（去掉文件名）
            physical_dir = str(Path(path).parent).replace('\\', '/')
            tags = n.get('tags', [])
            processing_path = n.get('processing_path', '')

            # 推断建议目录
            suggested_dir = None
            max_matches = 0

            # 遍历 tag_patterns，找到最多匹配的规则
            for pattern in tag_patterns:
                pattern_tags = set(pattern.get('tags', []))
                file_tags = set(tags)
                matches = len(pattern_tags & file_tags)

                if matches >= 2 and matches > max_matches:
                    max_matches = matches
                    suggested_dir = pattern.get('suggested_dir')

            # 如果无精确匹配，使用 fallback
            if not suggested_dir and processing_path:
                suggested_dir = fallback_map.get(processing_path)

            # 检查对齐
            if suggested_dir and physical_dir != suggested_dir:
                err("l3_directory_misalignment",
                    f"{path}: 当前在 {physical_dir}，建议移至 {suggested_dir} (匹配 {max_matches} 个标签)")

    except Exception as e:
        err("l3_directory_inference", f"无法读取 l3-directory-inference.yaml: {e}")

# === 输出 ===
if errors:
    print(f"CONFIG SYNC FAILED — {len(errors)} issue(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("CONFIG SYNC OK — all checks passed")
    sys.exit(0)
