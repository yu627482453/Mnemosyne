#!/usr/bin/env python3
"""查询知识库（L3 topic 优先 → L2 → L1）"""
import argparse
import json
import sqlite3
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, Dict, Any

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"
QUERY_HISTORY_PATH = Path(__file__).parent.parent / ".query_history.jsonl"
HOT_MD_PATH = Path(__file__).parent.parent / "hot.md"

# 缓存失效机制：记录DB文件的最后修改时间
_last_db_mtime: float | None = None

# 查询计数器：每10次查询更新一次hot.md
_query_count: int = 0


def _check_and_clear_cache_if_stale():
    """检查DB文件是否更新，如果更新则清空query缓存"""
    global _last_db_mtime

    if not DB_PATH.exists():
        return

    current_mtime = DB_PATH.stat().st_mtime

    if _last_db_mtime is None:
        _last_db_mtime = current_mtime
        return

    if current_mtime != _last_db_mtime:
        # DB已更新，清空缓存
        _query_cached.cache_clear()
        _last_db_mtime = current_mtime


def _record_query_history(keyword: str, results: List[Tuple[str, str, str, str]]):
    """记录查询历史到JSONL文件（追加模式）"""
    record = {
        "timestamp": time.time(),
        "keyword": keyword,
        "results": [r[0] for r in results]  # 只记录path
    }

    try:
        with open(QUERY_HISTORY_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except Exception:
        pass  # 记录失败不影响查询功能


def _update_hot_md():
    """从查询历史更新hot.md（最近72h的top20页面）"""
    if not QUERY_HISTORY_PATH.exists():
        return

    # 72小时前的时间戳
    cutoff_time = time.time() - 72 * 3600
    page_counter = Counter()

    try:
        with open(QUERY_HISTORY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get('timestamp', 0) >= cutoff_time:
                        for path in record.get('results', []):
                            page_counter[path] += 1
                except json.JSONDecodeError:
                    continue

        # 生成hot.md内容
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        lines = [
            "# 热门页面（最近72h查询）\n",
            f"\n最后更新：{now}\n",
            "\n## Top 20 页面\n\n"
        ]

        for i, (path, count) in enumerate(page_counter.most_common(20), 1):
            # 从path提取slug作为wikilink
            slug = Path(path).stem
            lines.append(f"{i}. [[{slug}]] (查询{count}次)\n")

        if not page_counter:
            lines.append("暂无查询记录\n")

        HOT_MD_PATH.write_text(''.join(lines), encoding='utf-8')
    except Exception:
        pass  # 更新失败不影响查询功能


@lru_cache(maxsize=128)
def _query_cached(
    keyword: str,
    limit: int,
    layer: str | None,
    kind: str | None,
    topic: str | None,
) -> tuple:
    """内部缓存的查询函数（返回tuple以便缓存）"""
    return tuple(_query_impl(keyword, limit, layer, kind, topic))


def query(
    keyword: str,
    limit: int = 8,
    layer: str | None = None,
    kind: str | None = None,
    topic: str | None = None,
) -> List[Tuple[str, str, str, str]]:
    """查询知识库，返回 (path, title, summary, layer) 列表（带缓存+历史记录）"""
    global _query_count

    _check_and_clear_cache_if_stale()
    results = list(_query_cached(keyword, limit, layer, kind, topic))

    # 记录查询历史
    if results:
        _record_query_history(keyword, results)
        _query_count += 1

        # 每10次查询更新一次hot.md
        if _query_count % 10 == 0:
            _update_hot_md()

    return results


def _query_impl(
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

    # 1. L3 topic 优先（结合文本相关性70%+入链数量30%）
    cur.execute(
        f"""
        SELECT n.path, n.title, n.summary, n.layer
        FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
        WHERE notes_fts MATCH ? AND n.path LIKE '0101-wiki-topics/%'{filter_clause}
        ORDER BY (
            f.rank * 0.7 +
            (SELECT COUNT(*) FROM wikilinks WHERE target_path=n.path) * 0.3
        ) LIMIT ?
    """,
        (keyword, *params, limit),
    )
    results = cur.fetchall()

    # 2. L3 concept/entity/comparison（结合文本相关性70%+入链数量30%）
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ?
            AND (n.path LIKE '0102-wiki-concepts/%' OR n.path LIKE '0103-wiki-entities/%'
                 OR n.path LIKE '0104-wiki-comparisons/%'){filter_clause}
            ORDER BY (
                f.rank * 0.7 +
                (SELECT COUNT(*) FROM wikilinks WHERE target_path=n.path) * 0.3
            ) LIMIT ?
        """,
            (keyword, *params, limit - len(results)),
        )
        results.extend(cur.fetchall())

    # 3. L2（结合文本相关性70%+入链数量30%）
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L2'{filter_clause}
            ORDER BY (
                f.rank * 0.7 +
                (SELECT COUNT(*) FROM wikilinks WHERE target_path=n.path) * 0.3
            ) LIMIT ?
        """,
            (keyword, *params, limit - len(results)),
        )
        results.extend(cur.fetchall())

    # 4. L1（结合文本相关性70%+入链数量30%）
    if len(results) < limit:
        cur.execute(
            f"""
            SELECT n.path, n.title, n.summary, n.layer
            FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
            WHERE notes_fts MATCH ? AND n.layer = 'L1'{filter_clause}
            ORDER BY (
                f.rank * 0.7 +
                (SELECT COUNT(*) FROM wikilinks WHERE target_path=n.path) * 0.3
            ) LIMIT ?
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
