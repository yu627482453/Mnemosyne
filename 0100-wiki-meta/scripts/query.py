#!/usr/bin/env python3
"""查询知识库（L3 topic 优先 → L2 → L1）"""
import argparse
import json
import logging
import sqlite3
import sys
import time
from collections import Counter
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, Dict, Any, Literal, Optional

# 配置日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 类型别名
Layer = Literal["L1", "L2", "L3"]
Kind = Literal["standard", "topic", "concept", "entity", "comparison"]
QueryResult = Tuple[str, str, str, str]  # (path, title, summary, layer)

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"
QUERY_HISTORY_PATH = Path(__file__).parent.parent / ".query_history.jsonl"
HOT_MD_PATH = Path(__file__).parent.parent / "hot.md"

# 缓存失效机制：记录DB文件的最后修改时间
_last_db_mtime: Optional[float] = None

# 查询计数器：每10次查询更新一次hot.md
_query_count: int = 0


@contextmanager
def get_db_connection():
    """数据库连接管理器（自动关闭连接）"""
    if not DB_PATH.exists():
        logger.error(f"数据库不存在: {DB_PATH}")
        raise FileNotFoundError(
            f"数据库未初始化，请运行: python {Path(__file__).parent / 'init-db.py'}"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    except Exception as e:
        logger.exception(f"数据库操作失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


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


def _record_query_history(keyword: str, results: List[QueryResult]):
    """记录查询历史到JSONL文件（追加模式）- 记录完整结果用于推荐"""
    record = {
        "timestamp": time.time(),
        "keyword": keyword,
        "results": [
            {
                "path": r[0],
                "title": r[1],
                "layer": r[3],
                "rank": idx + 1  # 记录排名
            }
            for idx, r in enumerate(results)
        ]
    }

    try:
        with open(QUERY_HISTORY_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except OSError as e:
        logger.warning(f"记录查询历史失败: {e}")


def _update_hot_md():
    """从查询历史更新hot.md（最近72h的top20页面，按关键词聚合）"""
    if not QUERY_HISTORY_PATH.exists():
        return

    # 72小时前的时间戳
    cutoff_time = time.time() - 72 * 3600
    # 改为 {keyword: [(path, score)]} 结构
    keyword_pages: Dict[str, Counter] = {}

    try:
        with open(QUERY_HISTORY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get('timestamp', 0) >= cutoff_time:
                        kw = record.get('keyword', '')
                        if kw not in keyword_pages:
                            keyword_pages[kw] = Counter()

                        # 按排名加权：top1得分10，top2得分9...
                        for result in record.get('results', []):
                            path = result.get('path') if isinstance(result, dict) else result
                            rank = result.get('rank', 1) if isinstance(result, dict) else 1
                            score = max(11 - rank, 1)  # rank 1->10分, rank 10->1分
                            keyword_pages[kw][path] += score
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"跳过无效记录: {e}")
                    continue

        # 生成hot.md内容
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M')

        lines = [
            "# 热门页面（最近72h查询）\n",
            f"\n最后更新：{now}\n",
            "\n## 按关键词聚合\n\n"
        ]

        # 按查询频率排序关键词
        sorted_keywords = sorted(
            keyword_pages.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True
        )[:10]

        for keyword, pages in sorted_keywords:
            lines.append(f"### {keyword}\n\n")
            for path, score in pages.most_common(5):
                slug = Path(path).stem
                lines.append(f"- [[{slug}]] (得分{score})\n")
            lines.append("\n")

        if not keyword_pages:
            lines.append("暂无查询记录\n")

        HOT_MD_PATH.write_text(''.join(lines), encoding='utf-8')
    except OSError as e:
        logger.warning(f"更新hot.md失败: {e}")


@lru_cache(maxsize=256)
def _query_cached(
    keyword: str,
    limit: int,
) -> tuple:
    """内部缓存的查询函数（只缓存keyword和limit，提高命中率）"""
    return tuple(_query_impl(keyword, limit, None, None, None))


def query(
    keyword: str,
    limit: int = 8,
    layer: Optional[Layer] = None,
    kind: Optional[Kind] = None,
    topic: Optional[str] = None,
) -> List[QueryResult]:
    """查询知识库，返回 (path, title, summary, layer) 列表（带缓存+历史记录+后过滤）"""
    global _query_count

    _check_and_clear_cache_if_stale()

    # 缓存只用keyword和limit，其他参数后过滤
    all_results = list(_query_cached(keyword, limit * 3))  # 预取3倍结果用于过滤

    # 后过滤
    filtered = all_results
    if layer:
        filtered = [r for r in filtered if r[3] == layer]
    if kind:
        # 需要从数据库再查一次kind字段（简化版：暂不支持kind过滤缓存结果）
        filtered = _filter_by_kind(filtered, kind)
    if topic:
        filtered = _filter_by_topic(filtered, topic)

    results = filtered[:limit]

    # 记录查询历史
    if results:
        _record_query_history(keyword, results)
        _query_count += 1

        # 每5次查询更新一次hot.md（提高缓存及时性）
        if _query_count % 5 == 0:
            _update_hot_md()

    return results


def _filter_by_kind(results: List[QueryResult], kind: Kind) -> List[QueryResult]:
    """根据kind过滤结果（需要额外查询数据库）"""
    if not results:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            paths = [r[0] for r in results]
            placeholders = ','.join('?' * len(paths))
            cur.execute(
                f"SELECT path FROM notes WHERE path IN ({placeholders}) AND kind = ?",
                (*paths, kind)
            )
            valid_paths = {row[0] for row in cur.fetchall()}
            return [r for r in results if r[0] in valid_paths]
    except sqlite3.Error as e:
        logger.error(f"kind过滤失败: {e}")
        return results


def _filter_by_topic(results: List[QueryResult], topic: str) -> List[QueryResult]:
    """根据topic过滤结果（需要额外查询数据库）"""
    if not results:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            paths = [r[0] for r in results]
            placeholders = ','.join('?' * len(paths))
            cur.execute(
                f"SELECT path FROM notes WHERE path IN ({placeholders}) AND topic = ?",
                (*paths, topic)
            )
            valid_paths = {row[0] for row in cur.fetchall()}
            return [r for r in results if r[0] in valid_paths]
    except sqlite3.Error as e:
        logger.error(f"topic过滤失败: {e}")
        return results


def _query_impl(
    keyword: str,
    limit: int = 8,
    layer: Optional[Layer] = None,
    kind: Optional[Kind] = None,
    topic: Optional[str] = None,
) -> List[QueryResult]:
    """查询知识库（统一UNION查询 + 修复排序算法）"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # 统一UNION查询，用CASE WHEN实现分层优先级
            # 多因子排序：文本相关性 + 入链数 + 新鲜度 + 质量
            cur.execute("""
                WITH ranked_results AS (
                    SELECT
                        n.path,
                        n.title,
                        n.summary,
                        n.layer,
                        -f.rank as fts_score,
                        (SELECT COUNT(*) FROM wikilinks WHERE target_path = n.path) as inbound_count,
                        CASE
                            WHEN n.path LIKE '0101-wiki-topics/%' THEN 1
                            WHEN n.path LIKE '0102-wiki-concepts/%'
                                OR n.path LIKE '0103-wiki-entities/%'
                                OR n.path LIKE '0104-wiki-comparisons/%' THEN 2
                            WHEN n.layer = 'L2' THEN 3
                            WHEN n.layer = 'L1' THEN 4
                            ELSE 5
                        END as layer_priority,
                        -- 新鲜度得分：30天内=1.0，90天内=0.5，更久=0.2
                        CASE
                            WHEN julianday('now') - julianday(n.updated) <= 30 THEN 1.0
                            WHEN julianday('now') - julianday(n.updated) <= 90 THEN 0.5
                            ELSE 0.2
                        END as freshness_score,
                        -- 质量得分：published=1.0，draft=0.7
                        CASE
                            WHEN n.status = 'published' THEN 1.0
                            WHEN n.status = 'draft' THEN 0.7
                            ELSE 0.5
                        END as quality_score
                    FROM notes_fts f
                    JOIN notes n ON f.rowid = n.rowid
                    WHERE notes_fts MATCH ?
                )
                SELECT path, title, summary, layer
                FROM ranked_results
                ORDER BY
                    layer_priority,
                    (fts_score * 0.5 + inbound_count * 0.25 + freshness_score * 0.15 + quality_score * 0.1) DESC
                LIMIT ?
            """, (keyword, limit))

            results = cur.fetchall()
            return results
    except sqlite3.Error as e:
        logger.error(f"查询失败: {e}")
        return []


def get_backlinks(target_path: str) -> List[Tuple[str, str]]:
    """查询反向链接：哪些页面链接到了目标页面"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
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
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error(f"查询反向链接失败: {e}")
        return []


def get_dead_links() -> List[Tuple[str, str, int]]:
    """检测死链：target_path 为 NULL 的 wikilink"""
    try:
        with get_db_connection() as conn:
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
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error(f"查询死链失败: {e}")
        return []


def get_stats() -> Dict[str, Any]:
    """获取知识库统计信息"""
    try:
        with get_db_connection() as conn:
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

            return stats
    except sqlite3.Error as e:
        logger.error(f"获取统计信息失败: {e}")
        return {}


def query_graph(
    keyword: str,
    max_hops: int = 3,
    limit: int = 5
) -> Dict[str, Any]:
    """GraphRAG路径查询：结构化查询，返回路径和Hub节点推荐

    Args:
        keyword: 搜索关键词
        max_hops: 最大跳数（路径长度）
        limit: 返回的候选结果数量

    Returns:
        {
            "answer_type": "path" | "list" | "direct",
            "candidates": [{"path": str, "title": str, "score": float}],
            "path": [str],  # 多跳路径（如果存在）
            "hub_nodes": [str],  # Hub节点（高入链度）
            "should_read": [str]  # 推荐阅读的页面
        }
    """
    # 1. 先用常规query获取初始候选
    initial_results = query(keyword, limit=limit)

    if not initial_results:
        return {
            "answer_type": "gap",
            "candidates": [],
            "path": [],
            "hub_nodes": [],
            "should_read": []
        }

    # 2. 获取Hub节点（入链数top10）
    hub_nodes = _get_hub_nodes(limit=10)

    # 3. 构建候选结果列表
    candidates = [
        {
            "path": r[0],
            "title": r[1],
            "score": 1.0 - (i * 0.1)  # 简单的递减得分
        }
        for i, r in enumerate(initial_results)
    ]

    # 4. 生成should_read列表（初始结果+相关Hub节点）
    should_read = [r[0] for r in initial_results[:3]]

    # 用FTS5查询相关Hub节点（而非简单字符串包含）
    relevant_hubs = _find_relevant_hubs(keyword, hub_nodes, limit=2)
    should_read.extend(relevant_hubs)

    # 尝试查找top2候选之间的路径
    path = []
    if len(initial_results) >= 2:
        path = _bfs_find_path(
            initial_results[0][0],
            initial_results[1][0],
            max_hops=max_hops
        )

    return {
        "answer_type": "path" if path else "list",
        "candidates": candidates,
        "path": path,
        "hub_nodes": hub_nodes,
        "should_read": should_read[:5]
    }


def _get_hub_nodes(limit: int = 10) -> List[str]:
    """获取Hub节点（高入链度的页面）"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT n.path, n.title, COUNT(w.source_path) as inbound_count
                FROM notes n
                JOIN wikilinks w ON w.target_path = n.path
                WHERE n.layer = 'L3'
                GROUP BY n.path
                ORDER BY inbound_count DESC
                LIMIT ?
            """, (limit,))
            results = cur.fetchall()
            return [r[0] for r in results]
    except sqlite3.Error as e:
        logger.error(f"获取Hub节点失败: {e}")
        return []


def _bfs_find_path(start_path: str, end_path: str, max_hops: int = 3) -> List[str]:
    """BFS查找两个页面间的最短路径"""
    if start_path == end_path:
        return [start_path]

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # BFS队列：(当前路径, 已访问集合)
            from collections import deque
            queue = deque([([start_path], {start_path})])

            while queue:
                current_path, visited = queue.popleft()

                # 超过最大跳数
                if len(current_path) > max_hops:
                    continue

                current_node = current_path[-1]

                # 查询当前节点的所有出链
                cur.execute("""
                    SELECT target_path FROM wikilinks
                    WHERE source_path = ? AND target_path IS NOT NULL
                """, (current_node,))

                for (neighbor,) in cur.fetchall():
                    if neighbor == end_path:
                        return current_path + [neighbor]

                    if neighbor not in visited:
                        new_visited = visited | {neighbor}
                        queue.append((current_path + [neighbor], new_visited))

            return []  # 未找到路径
    except sqlite3.Error as e:
        logger.error(f"BFS路径查找失败: {e}")
        return []


def _find_relevant_hubs(keyword: str, hub_paths: List[str], limit: int = 2) -> List[str]:
    """用FTS5查询与关键词相关的Hub节点"""
    if not hub_paths:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholders = ','.join('?' * len(hub_paths))
            cur.execute(f"""
                SELECT n.path, -f.rank as score
                FROM notes_fts f
                JOIN notes n ON f.rowid = n.rowid
                WHERE notes_fts MATCH ? AND n.path IN ({placeholders})
                ORDER BY score DESC
                LIMIT ?
            """, (keyword, *hub_paths, limit))
            return [row[0] for row in cur.fetchall()]
    except sqlite3.Error as e:
        logger.warning(f"查询相关Hub失败，降级到字符串匹配: {e}")
        # 降级方案：字符串包含匹配
        return [h for h in hub_paths if keyword.lower() in h.lower()][:limit]


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
    if not args.keyword or not args.keyword.strip():
        print("错误: 关键词不能为空\n")
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
