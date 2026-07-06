#!/usr/bin/env python3
"""查询知识库（L3 topic 优先 → L2 → L1）"""
import argparse
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"


def query(
    keyword: str,
    limit: int = 8,
    layer: str | None = None,
    kind: str | None = None,
    topic: str | None = None,
) -> List[Tuple[str, str, str, str]]:
    """查询知识库，返回 (path, title, summary, layer) 列表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    results = []

    # 构建基础过滤条件
    filters = []
    params = []
    if layer:
        filters.append("n.layer = ?")
        params.append(layer)
    if kind:
        filters.append("n.kind = ?")
        params.append(kind)
    if topic:
        filters.append("n.topic = ?")
        params.append(topic)

    filter_clause = f" AND {' AND '.join(filters)}" if filters else ""

    # 1. L3 topic 优先
    cur.execute(
        f"""
        SELECT n.path, n.title, n.summary, n.layer
        FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
        WHERE notes_fts MATCH ? AND n.path LIKE '0101-wiki-topics/%'{filter_clause}
        ORDER BY f.rank LIMIT ?
    """,
        (keyword, *params, limit),
    )
    results = cur.fetchall()

    # 2. L3 concept/entity/comparison
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ?
            AND (n.path LIKE '0102-wiki-concepts/%' OR n.path LIKE '0103-wiki-entities/%'
                 OR n.path LIKE '0104-wiki-comparisons/%'){filter_clause}
            ORDER BY f.rank LIMIT ?
        """,
            (keyword, *params, limit - len(results)),
        )
        results.extend(cur.fetchall())

    # 3. L2
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L2'{filter_clause}
            ORDER BY f.rank LIMIT ?
        """,
            (keyword, *params, limit - len(results)),
        )
        results.extend(cur.fetchall())

    # 4. L1
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L1'{filter_clause}
            ORDER BY f.rank LIMIT ?
        """,
            (keyword, *params, limit - len(results)),
        )
        results.extend(cur.fetchall())

    conn.close()
    return results[:limit]


def get_backlinks(target_path: str) -> List[Tuple[str, str]]:
    """查询反向链接：哪些页面链接到了目标页面"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # 从 wikilinks 表查询
    cur.execute(
        """
        SELECT DISTINCT w.source_path, n.title
        FROM wikilinks w
        LEFT JOIN notes n ON w.source_path = n.path
        WHERE w.target_path = ?
        ORDER BY w.source_path
    """,
        (target_path,),
    )
    results = cur.fetchall()
    conn.close()
    return results


def get_dead_links() -> List[Tuple[str, str, str]]:
    """检测死链：target_path 为 NULL 的 wikilink"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT source_path, target_slug, COUNT(*) as cnt
        FROM wikilinks
        WHERE target_path IS NULL AND link_type = 'wikilink'
        GROUP BY source_path, target_slug
        ORDER BY source_path, target_slug
    """
    )
    results = cur.fetchall()
    conn.close()
    return results


def get_stats() -> Dict[str, Any]:
    """获取知识库统计信息"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    stats = {}

    # 按层级统计
    cur.execute("SELECT layer, COUNT(*) FROM notes GROUP BY layer")
    stats["by_layer"] = dict(cur.fetchall())

    # 按类型统计
    cur.execute("SELECT kind, COUNT(*) FROM notes WHERE kind IS NOT NULL GROUP BY kind")
    stats["by_kind"] = dict(cur.fetchall())

    # 按主题统计
    cur.execute(
        "SELECT topic, COUNT(*) FROM notes WHERE topic IS NOT NULL GROUP BY topic ORDER BY COUNT(*) DESC LIMIT 10"
    )
    stats["top_topics"] = cur.fetchall()

    # 总链接数
    cur.execute("SELECT COUNT(*) FROM wikilinks")
    stats["total_links"] = cur.fetchone()[0]

    # 死链数
    cur.execute(
        "SELECT COUNT(*) FROM wikilinks WHERE target_path IS NULL AND link_type = 'wikilink'"
    )
    stats["dead_links"] = cur.fetchone()[0]

    conn.close()
    return stats


def main():
    parser = argparse.ArgumentParser(description="查询知识库（L3 topic 优先 → L2 → L1）")
    parser.add_argument("keyword", nargs="?", help="搜索关键词")
    parser.add_argument("-l", "--limit", type=int, default=8, help="返回结果数量（默认8）")
    parser.add_argument("--layer", choices=["L1", "L2", "L3"], help="过滤层级")
    parser.add_argument("--kind", help="过滤类型（concept/entity/comparison/standard）")
    parser.add_argument("--topic", help="过滤主题")
    parser.add_argument("--backlinks", metavar="PATH", help="查询反向链接：哪些页面链接到指定路径")
    parser.add_argument("--dead-links", action="store_true", help="检测死链")
    parser.add_argument("--stats", action="store_true", help="显示知识库统计信息")

    args = parser.parse_args()

    # 统计模式
    if args.stats:
        stats = get_stats()
        print("\n=== 知识库统计 ===\n")
        print("按层级:")
        for layer, count in stats["by_layer"].items():
            print(f"  {layer}: {count}")
        print("\n按类型:")
        for kind, count in stats["by_kind"].items():
            print(f"  {kind}: {count}")
        print("\nTop 10 主题:")
        for topic, count in stats["top_topics"]:
            print(f"  {topic}: {count}")
        print(f"\n总链接数: {stats['total_links']}")
        print(f"死链数: {stats['dead_links']}")
        return

    # 死链检测模式
    if args.dead_links:
        dead = get_dead_links()
        if not dead:
            print("✓ 未发现死链")
            return
        print(f"\n发现 {len(dead)} 个死链：\n")
        for source, slug, cnt in dead:
            print(f"  {source} → [[{slug}]] (x{cnt})")
        return

    # 反向链接模式
    if args.backlinks:
        backlinks = get_backlinks(args.backlinks)
        if not backlinks:
            print(f"未找到链接到 '{args.backlinks}' 的页面")
            return
        print(f"\n找到 {len(backlinks)} 个反向链接：\n")
        for source, title in backlinks:
            title_display = title if title else "(无标题)"
            print(f"  {source} - {title_display}")
        return

    # 关键词查询模式
    if not args.keyword:
        parser.print_help()
        sys.exit(1)

    results = query(
        args.keyword,
        limit=args.limit,
        layer=args.layer,
        kind=args.kind,
        topic=args.topic,
    )

    if not results:
        print(f"未找到匹配 '{args.keyword}' 的笔记")
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
