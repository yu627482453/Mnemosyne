#!/usr/bin/env python3
"""索引所有笔记到 SQLite 数据库"""
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

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


def extract_wikilinks(md_file: Path) -> list[tuple[str, str | None]]:
    """提取 [[wikilink]]，返回 [(slug, resolved_path), ...]"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有 [[wikilink]]（不含 | 和 # 后的部分）
        links = re.findall(r'\[\[([^\]|#]+)', content)
        results = []

        for slug in links:
            slug = slug.strip()
            # 尝试解析为实际路径
            target_path = None
            for candidate in WIKI_ROOT.rglob(f"{slug}.md"):
                rel = str(candidate.relative_to(WIKI_ROOT)).replace('\\', '/')
                if '.trash' not in rel and '.git' not in rel:
                    target_path = rel
                    break
            results.append((slug, target_path))

        return results
    except Exception:
        return []


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
    """增量索引所有笔记到 SQLite"""
    conn = sqlite3.connect(DB_PATH, detect_types=0)
    cur = conn.cursor()

    # 获取当前索引状态（path → updated）
    cur.execute("SELECT path, updated FROM notes")
    indexed = {row[0]: str(row[1]) for row in cur.fetchall()}

    sync_topics(cur)

    added = updated_count = deleted = 0
    current_paths = set()

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
        current_paths.add(rel_path)
        file_updated = str(meta.get('updated', ''))

        # 跳过未变更的文件
        if rel_path in indexed and indexed[rel_path] == file_updated:
            continue

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

        # E4: 提取置信度和来源标注
        confidence = meta.get('confidence')
        provenance = meta.get('provenance')

        if confidence is not None:
            layer_data['confidence'] = confidence

        if provenance is not None:
            layer_data['provenance'] = provenance

        updated = meta.get('updated') or datetime.now().strftime('%Y-%m-%d')

        # 将 updated 字段转为时间戳（笔记实际更新时间，非索引执行时间）
        updated_str = str(updated) if updated else ''
        try:
            updated_ts = int(datetime.strptime(updated_str, '%Y-%m-%d').timestamp())
        except (ValueError, TypeError):
            updated_ts = 0

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
            updated_str if updated_str else None,
            updated_ts,
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

        # 提取 wikilinks 并填充 wikilinks 表
        wikilinks = extract_wikilinks(md_file)
        for slug, target_path in wikilinks:
            cur.execute("""
                INSERT OR IGNORE INTO wikilinks (source_path, target_slug, target_path, link_type)
                VALUES (?, ?, ?, 'wikilink')
            """, (rel_path, slug, target_path))

        # L3 反向索引：填充 file_produces 表
        if layer == 'L3':
            sources = meta.get('source') or []
            if isinstance(sources, str):
                sources = [sources]
            for src_path in sources:
                # 查找对应 L2 的 ingested_files 记录
                cur.execute(
                    "SELECT id FROM ingested_files WHERE source_path LIKE ?",
                    (f"%{src_path}%",)
                )
                row = cur.fetchone()
                if row:
                    cur.execute("""
                        INSERT OR IGNORE INTO file_produces
                        (source_file_id, produced_page_path, page_layer)
                        VALUES (?, ?, 'L3')
                    """, (row[0], rel_path))

        # 统计新增或更新
        if rel_path in indexed:
            updated_count += 1
        else:
            added += 1

    # 清理已删除文件的过期索引
    stale = set(indexed.keys()) - current_paths
    for path in stale:
        cur.execute("DELETE FROM notes WHERE path = ?", (path,))
        deleted += 1

    conn.commit()
    conn.close()
    print(f"索引完成：新增 {added}，更新 {updated_count}，删除 {deleted}")


if __name__ == "__main__":
    index_notes()
