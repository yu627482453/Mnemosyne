#!/usr/bin/env python3
"""索引所有笔记到 SQLite 数据库"""
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"
WIKI_ROOT = Path(__file__).parent.parent.parent

def parse_frontmatter(path: Path) -> dict | None:
    """解析 Frontmatter"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.startswith('---'):
            return None
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        yaml_text = match.group(1)
        meta = {}
        for line in yaml_text.split('\n'):
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
            meta[key] = val
        return meta
    except Exception:
        return None

def index_notes():
    """索引所有笔记"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM note_tags")
    cur.execute("DELETE FROM notes")

    indexed = 0
    for md_file in WIKI_ROOT.rglob("*.md"):
        if any(p in md_file.parts for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta']):
            continue

        meta = parse_frontmatter(md_file)
        if not meta:
            continue

        layer = meta.get('layer', 'L1')
        if layer not in ['L1', 'L2', 'L3']:
            continue

        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        layer_data = {}
        if layer == 'L2':
            layer_data = {
                'topic': meta.get('topic'),
                'source': meta.get('source'),
                'source_url': meta.get('source_url'),
                'resource_refs': meta.get('resource_refs', [])
            }
        elif layer == 'L3':
            layer_data = {
                'processing_path': meta.get('processing_path'),
                'source': meta.get('source', [])
            }
            if meta.get('kind') == 'entity':
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
            updated,
            int(datetime.now().timestamp()),
            json.dumps(layer_data, ensure_ascii=False)
        ))

        tags = meta.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                cur.execute("INSERT OR IGNORE INTO tags (tag) VALUES (?)", (tag,))
                cur.execute("INSERT OR IGNORE INTO note_tags (note_path, tag) VALUES (?, ?)",
                           (rel_path, tag))

        indexed += 1

    conn.commit()
    conn.close()
    print(f"Indexed {indexed} notes")

if __name__ == "__main__":
    index_notes()
