#!/usr/bin/env python3
"""索引所有笔记到 SQLite 数据库"""
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

import yaml

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"
WIKI_ROOT = Path(__file__).parent.parent.parent


def parse_frontmatter(path: Path) -> dict | None:
    """使用标准 yaml 解析 Frontmatter"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.startswith('---'):
            return None
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return None


def sync_topics(cur):
    """同步 topics.yaml 到数据库（active topic 单独落行，display_name 使用 topic 编号+名）"""
    topics_file = WIKI_ROOT / "0100-wiki-meta" / "configs" / "topics.yaml"
    if not topics_file.exists():
        return
    with open(topics_file, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    cur.execute("DELETE FROM topics")
    for domain_name, domain_data in (cfg.get('domains') or {}).items():
        rng = domain_data.get('range', [0, 9999])
        # 写入大类行（作为分类容器）
        cur.execute("""
            INSERT INTO topics (topic_dir, display_name, category, range_start, range_end)
            VALUES (?, ?, ?, ?, ?)
        """, (domain_name, domain_name, domain_name, rng[0], rng[1]))
        # 写入每个 active topic（topic_dir = 3000-Agent, display_name = Agent）
        for topic_id in (domain_data.get('active') or []):
            m = re.match(r'^(\d{4})-(.+)$', topic_id)
            if not m:
                continue
            display = m.group(2)
            cur.execute("""
                INSERT OR REPLACE INTO topics (topic_dir, display_name, category, range_start, range_end)
                VALUES (?, ?, ?, ?, ?)
            """, (topic_id, display, domain_name, rng[0], rng[1]))


def index_notes():
    """索引所有笔记到 SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 先清空关联表再清空主表，避免外键约束冲突
    cur.execute("DELETE FROM note_tags")
    cur.execute("DELETE FROM tags")
    cur.execute("DELETE FROM notes")

    sync_topics(cur)

    indexed = 0
    for md_file in WIKI_ROOT.rglob("*.md"):
        if any(p in md_file.parts for p in ['.trash', '.git', '0000-meta', '0001-resource', '0003-inbox', '0100-wiki-meta', '0109-log']):
            continue

        meta = parse_frontmatter(md_file)
        if not meta:
            continue

        layer = meta.get('layer')
        if layer not in ['L2', 'L3']:
            continue

        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        layer_data = {}
        if layer == 'L2':
            layer_data = {
                'topic': meta.get('topic'),
                'id': meta.get('id'),
                'content_hash': meta.get('content_hash'),
                'source': meta.get('source'),
                'source_url': meta.get('source_url'),
                'resource_refs': meta.get('resource_refs', []) or [],
                'planned_links': meta.get('planned_links', []) or [],
                'aliases': meta.get('aliases', []) or [],
            }
        elif layer == 'L3':
            layer_data = {
                'processing_path': meta.get('processing_path'),
                'source': meta.get('source', []) or [],
            }
            if meta.get('kind') == 'topic':
                layer_data['topic'] = meta.get('topic')
            elif meta.get('kind') == 'entity':
                layer_data['entity_type'] = meta.get('entity_type')
            elif meta.get('kind') == 'comparison':
                layer_data['comparison_axis'] = meta.get('comparison_axis')
                layer_data['lhs'] = meta.get('lhs')
                layer_data['rhs'] = meta.get('rhs')

        updated = meta.get('updated') or datetime.now().strftime('%Y-%m-%d')
        cur.execute("""
            INSERT OR REPLACE INTO notes
            (path, title, layer, kind, status, summary, created, updated, updated_ts, layer_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rel_path,
            meta.get('title', ''),
            layer,
            meta.get('kind'),
            meta.get('status'),
            meta.get('summary'),
            meta.get('created'),
            str(updated) if updated else None,
            int(datetime.now().timestamp()),
            json.dumps(layer_data, ensure_ascii=False)
        ))

        tags = meta.get('tags') or []
        if isinstance(tags, list):
            for tag in tags:
                if not isinstance(tag, str):
                    continue
                # 插入标签（仅记录 tag 名称，元数据由其他脚本同步）
                cur.execute("INSERT OR IGNORE INTO tags (tag) VALUES (?)", (tag,))
                cur.execute("""
                    INSERT OR IGNORE INTO note_tags (note_path, tag) VALUES (?, ?)
                """, (rel_path, tag))

        indexed += 1

    conn.commit()
    conn.close()
    print(f"Indexed {indexed} notes")


if __name__ == "__main__":
    index_notes()
