#!/usr/bin/env python3
"""知识图谱分析工具 - E5关系类型化分析"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"


def analyze_typed_relationships():
    """分析类型化关系模式（E5）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== E5 类型化关系分析 ===\n")

    # 1. 最常被uses的概念 → 基础组件
    print("## 1. 最常被使用的基础组件（uses关系）")
    cur.execute("""
        SELECT target_path, COUNT(*) as usage_count
        FROM relationships
        WHERE rel_type = 'uses' AND target_path IS NOT NULL
        GROUP BY target_path
        ORDER BY usage_count DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    if results:
        for path, count in results:
            print(f"  {count}x ← {path}")
    else:
        print("  （暂无uses关系）")

    # 2. 技术演进链（replaces关系）
    print("\n## 2. 技术演进链（X替代Y）")
    cur.execute("""
        SELECT source_path, target_path
        FROM relationships
        WHERE rel_type = 'replaces' AND target_path IS NOT NULL
        ORDER BY source_path
    """)
    results = cur.fetchall()
    if results:
        for src, tgt in results:
            print(f"  {src} → {tgt}")
    else:
        print("  （暂无replaces关系）")

    # 3. 对立概念对（contradicts关系）
    print("\n## 3. 对立概念对")
    cur.execute("""
        SELECT source_path, target_path
        FROM relationships
        WHERE rel_type = 'contradicts' AND target_path IS NOT NULL
        ORDER BY source_path
    """)
    results = cur.fetchall()
    if results:
        for src, tgt in results:
            print(f"  {src} ⚔ {tgt}")
    else:
        print("  （暂无contradicts关系）")

    # 4. 关系类型统计
    print("\n## 4. 关系类型统计")
    cur.execute("""
        SELECT rel_type, COUNT(*) as count
        FROM relationships
        WHERE target_path IS NOT NULL
        GROUP BY rel_type
        ORDER BY count DESC
    """)
    results = cur.fetchall()
    if results:
        for rel_type, count in results:
            print(f"  {rel_type}: {count}")
    else:
        print("  （暂无关系数据）")

    conn.close()


def main():
    """主入口"""
    if not DB_PATH.exists():
        print(f"错误：数据库不存在 {DB_PATH}")
        print("请先运行 init-db.py 和 index-notes.py")
        return 1

    analyze_typed_relationships()
    return 0


if __name__ == "__main__":
    exit(main())
