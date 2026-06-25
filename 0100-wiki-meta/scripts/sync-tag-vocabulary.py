#!/usr/bin/env python3
"""同步标签词表到 SQLite（从 tag-vocabulary.yaml）"""
import sqlite3
from pathlib import Path
import yaml

WIKI_ROOT = Path(__file__).parent.parent.parent
DB_PATH = WIKI_ROOT / ".wiki.db"
TAG_VOCAB_PATH = WIKI_ROOT / "0100-wiki-meta" / "configs" / "tag-vocabulary.yaml"


def sync_tag_vocabulary():
    """从 tag-vocabulary.yaml 同步标签元数据到 SQLite

    功能：
    1. 同步标签元数据（tag_zh, category, description, aliases）
    2. 从 note_tags 计算 usage_count
    3. 清理 note_tags 中不存在于词表的标签
    4. 清理 tags 中不存在于词表的标签
    """

    # 读取标签词表
    with open(TAG_VOCAB_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    vocab = data.get('vocabulary') or []
    valid_tags = {entry.get('tag_en') for entry in vocab if entry.get('tag_en')}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 清理 note_tags 中不在词表的标签
    cur.execute("SELECT DISTINCT tag FROM note_tags")
    used_tags = {row[0] for row in cur.fetchall()}
    orphaned_tags = used_tags - valid_tags

    if orphaned_tags:
        placeholders = ','.join('?' * len(orphaned_tags))
        cur.execute(f"DELETE FROM note_tags WHERE tag IN ({placeholders})", list(orphaned_tags))
        print(f"  ✓ 清理 {len(orphaned_tags)} 个孤立标签引用")

    # 2. 清理 tags 表中不在词表的标签
    cur.execute("SELECT tag FROM tags")
    db_tags = {row[0] for row in cur.fetchall()}
    stale_tags = db_tags - valid_tags

    if stale_tags:
        placeholders = ','.join('?' * len(stale_tags))
        cur.execute(f"DELETE FROM tags WHERE tag IN ({placeholders})", list(stale_tags))
        print(f"  ✓ 清理 {len(stale_tags)} 个过时标签")

    # 3. 从 note_tags 计算 usage_count
    cur.execute("SELECT tag, COUNT(*) FROM note_tags GROUP BY tag")
    usage_counts = {tag: count for tag, count in cur.fetchall()}

    # 4. 更新或插入标签元数据
    updated = 0
    inserted = 0

    for entry in vocab:
        tag_en = entry.get('tag_en')
        if not tag_en:
            continue

        tag_zh = entry.get('tag_zh', '')
        aliases = ', '.join(entry.get('aliases', []))
        category = entry.get('category', '')
        description = entry.get('description', '')
        usage_count = usage_counts.get(tag_en, 0)

        # 尝试更新
        cur.execute("""
            UPDATE tags
            SET tag_zh = ?, aliases = ?, category = ?, description = ?, usage_count = ?
            WHERE tag = ?
        """, (tag_zh, aliases, category, description, usage_count, tag_en))

        if cur.rowcount == 0:
            # 插入新标签
            cur.execute("""
                INSERT INTO tags
                (tag, tag_en, tag_zh, language, aliases, category, description, usage_count, created)
                VALUES (?, ?, ?, 'en', ?, ?, ?, ?, CURRENT_DATE)
            """, (tag_en, tag_en, tag_zh, aliases, category, description, usage_count))
            inserted += 1
        else:
            updated += 1

    conn.commit()
    conn.close()

    print(f"✓ 同步完成: {updated} 更新, {inserted} 新增, {len(valid_tags)} 总计")


if __name__ == "__main__":
    sync_tag_vocabulary()
