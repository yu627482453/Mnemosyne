#!/usr/bin/env python3
"""查询知识库（L3 topic 优先 → L2 → L1）"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def query(keyword: str, limit: int = 8):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. L3 topic 优先
    cur.execute("""
        SELECT n.path, n.title, n.summary, n.layer
        FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
        WHERE notes_fts MATCH ? AND n.path LIKE '0101-wiki-topics/%'
        ORDER BY f.rank LIMIT ?
    """, (keyword, limit))
    results = cur.fetchall()

    # 2. L3 concept/entity/comparison
    if len(results) < limit:
        cur.execute("""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ?
            AND (n.path LIKE '0102-wiki-concepts/%' OR n.path LIKE '0103-wiki-entities/%' OR n.path LIKE '0104-wiki-comparisons/%')
            ORDER BY f.rank LIMIT ?
        """, (keyword, limit - len(results)))
        results.extend(cur.fetchall())

    # 3. L2
    if len(results) < limit:
        cur.execute("""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L2'
            ORDER BY f.rank LIMIT ?
        """, (keyword, limit - len(results)))
        results.extend(cur.fetchall())

    # 4. L1
    if len(results) < limit:
        cur.execute("""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L1'
            ORDER BY f.rank LIMIT ?
        """, (keyword, limit - len(results)))
        results.extend(cur.fetchall())

    conn.close()
    return results[:limit]

def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py <keyword> [limit]")
        sys.exit(1)

    keyword = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    results = query(keyword, limit)

    if not results:
        print(f"未找到匹配 '{keyword}' 的笔记")
        return

    print(f"\n找到 {len(results)} 条结果：\n")
    for path, title, summary, layer in results:
        print(f"[{layer}] {title}")
        print(f"    路径: {path}")
        if summary:
            print(f"    摘要: {summary[:100]}...")
        print()

if __name__ == "__main__":
    main()
