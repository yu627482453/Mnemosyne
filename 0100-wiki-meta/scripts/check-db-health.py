#!/usr/bin/env python3
"""知识库健康检查 - DB 驱动的聚合诊断"""
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta

WIKI_ROOT = Path(__file__).parent.parent.parent
DB_PATH = WIKI_ROOT / ".wiki.db"

# 严重性级别
CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

issues: List[Tuple[str, str, str]] = []  # (severity, category, message)


def err(severity: str, category: str, message: str):
    """记录问题"""
    issues.append((severity, category, message))


def check_orphaned_pages():
    """检查孤立页面（无入链，非入口页面）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # 查询无入链且非 topic/inbox 的页面
    cur.execute("""
        SELECT n.path, n.title, n.layer
        FROM notes n
        WHERE n.path NOT IN (SELECT DISTINCT target_path FROM wikilinks WHERE target_path IS NOT NULL)
        AND n.path NOT LIKE '0101-wiki-topics/%'
        AND n.path NOT LIKE '0003-inbox/%'
        AND n.path NOT LIKE '0105-wiki-base/%'
        AND n.layer IN ('L2', 'L3')
        ORDER BY n.layer, n.path
    """)
    orphans = cur.fetchall()
    conn.close()

    if orphans:
        for path, title, layer in orphans:
            err(INFO, "orphaned_page", f"[{layer}] {title} ({path}) 无入链")


def check_draft_stale():
    """检查过期 draft（>30天）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    cutoff = datetime.now() - timedelta(days=30)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    cur.execute("""
        SELECT path, title, updated
        FROM notes
        WHERE status = 'draft' AND updated < ?
        ORDER BY updated
    """, (cutoff_str,))
    stale = cur.fetchall()
    conn.close()

    if stale:
        for path, title, updated in stale:
            err(WARNING, "stale_draft", f"{title} ({path}) draft 超过 30 天（{updated}）")


def check_dead_links():
    """检查死链（wikilinks 中 target_path 为 NULL）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    cur.execute("""
        SELECT source_path, target_slug, COUNT(*) as cnt
        FROM wikilinks
        WHERE target_path IS NULL AND link_type = 'wikilink'
        GROUP BY source_path, target_slug
        ORDER BY cnt DESC
    """)
    dead = cur.fetchall()
    conn.close()

    if dead:
        for source, slug, cnt in dead:
            err(WARNING, "dead_link", f"{source} → [[{slug}]] (x{cnt})")


def check_l3_source_invalid():
    """检查 file_produces 表中的引用完整性"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # 检查 file_produces 中引用的 source_file_id 是否存在于 ingested_files
    cur.execute("""
        SELECT fp.produced_page_path, fp.source_file_id
        FROM file_produces fp
        LEFT JOIN ingested_files inf ON fp.source_file_id = inf.id
        WHERE inf.id IS NULL
    """)
    orphaned = cur.fetchall()
    conn.close()

    if orphaned:
        for page_path, file_id in orphaned:
            err(WARNING, "orphaned_produces", f"{page_path} 引用的源文件 ID {file_id} 不存在")


def get_dashboard_stats():
    """生成知识库仪表盘统计"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    stats = {}

    # 按层级统计
    cur.execute("SELECT layer, COUNT(*) FROM notes GROUP BY layer")
    stats["by_layer"] = dict(cur.fetchall())

    # 按状态统计
    cur.execute("SELECT status, COUNT(*) FROM notes WHERE status IS NOT NULL GROUP BY status")
    stats["by_status"] = dict(cur.fetchall())

    # 按类型统计（L3）
    cur.execute("SELECT kind, COUNT(*) FROM notes WHERE layer='L3' AND kind IS NOT NULL GROUP BY kind")
    stats["l3_by_kind"] = dict(cur.fetchall())

    # 总链接数和死链数
    cur.execute("SELECT COUNT(*) FROM wikilinks")
    stats["total_links"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM wikilinks WHERE target_path IS NULL AND link_type = 'wikilink'")
    stats["dead_links"] = cur.fetchone()[0]

    conn.close()
    return stats


def main():
    """运行所有健康检查并输出报告"""
    if not DB_PATH.exists():
        print("ERROR: .wiki.db 不存在，请先运行 index-notes.py")
        sys.exit(1)

    print("=== 知识库健康检查 ===\n")

    # 统计仪表盘
    stats = get_dashboard_stats()
    print("[STATS] 仪表盘统计")
    print(f"  总页面: {sum(stats['by_layer'].values())}")
    for layer, count in sorted(stats['by_layer'].items()):
        print(f"    {layer}: {count}")
    print(f"  总链接: {stats['total_links']}")
    print(f"  死链: {stats['dead_links']}")
    print()

    if stats.get('by_status'):
        print("  按状态:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
        print()

    if stats.get('l3_by_kind'):
        print("  L3 按类型:")
        for kind, count in sorted(stats['l3_by_kind'].items()):
            print(f"    {kind}: {count}")
        print()

    # 运行检查
    print("[CHECK] 运行健康检查...\n")
    check_orphaned_pages()
    check_draft_stale()
    check_dead_links()
    check_l3_source_invalid()

    # 汇总报告
    if not issues:
        print("[OK] 所有检查通过，知识库健康状态良好")
        sys.exit(0)

    # 按严重性分组
    by_severity = {CRITICAL: [], WARNING: [], INFO: []}
    for sev, cat, msg in issues:
        by_severity[sev].append((cat, msg))

    # 输出问题
    total = len(issues)
    print(f"[WARN] 发现 {total} 个问题：\n")

    if by_severity[CRITICAL]:
        print(f"[CRITICAL] ({len(by_severity[CRITICAL])})")
        for cat, msg in by_severity[CRITICAL]:
            print(f"  [{cat}] {msg}")
        print()

    if by_severity[WARNING]:
        print(f"[WARNING] ({len(by_severity[WARNING])})")
        for cat, msg in by_severity[WARNING]:
            print(f"  [{cat}] {msg}")
        print()

    if by_severity[INFO]:
        print(f"[INFO] ({len(by_severity[INFO])})")
        for cat, msg in by_severity[INFO]:
            print(f"  [{cat}] {msg}")
        print()

    # 退出状态：有 CRITICAL 则返回 2，有 WARNING 则返回 1，仅 INFO 则返回 0
    if by_severity[CRITICAL]:
        sys.exit(2)
    elif by_severity[WARNING]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
