#!/usr/bin/env python3
"""delta-track.py - Delta 跟踪工具（简化版）"""
import sys
import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def check_file(source_path):
    """检查文件是否已摄入"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT content_hash, ingested_at FROM ingested_files WHERE source_path = ?",
        (source_path,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        print(f"已摄入: {source_path}")
        print(f"  哈希: {result[0]}")
        print(f"  时间: {result[1]}")
        return 0
    else:
        print(f"未摄入: {source_path}")
        return 1

def record_ingestion(source_path, content_hash, l2_pages=None, l3_pages=None):
    """记录文件摄入结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 插入或更新文件记录
        cursor.execute(
            "INSERT OR REPLACE INTO ingested_files (source_path, content_hash) VALUES (?, ?)",
            (source_path, content_hash)
        )
        file_id = cursor.lastrowid

        # 记录产出的 L2 页面
        if l2_pages:
            for page in l2_pages.split(','):
                cursor.execute(
                    "INSERT OR IGNORE INTO file_produces (source_file_id, produced_page_path, page_layer) VALUES (?, ?, 'L2')",
                    (file_id, page.strip())
                )

        # 记录产出的 L3 页面
        if l3_pages:
            for page in l3_pages.split(','):
                cursor.execute(
                    "INSERT OR IGNORE INTO file_produces (source_file_id, produced_page_path, page_layer) VALUES (?, ?, 'L3')",
                    (file_id, page.strip())
                )

        conn.commit()
        print(f"✓ 已记录摄入: {source_path}")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"✗ 记录失败: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python delta-track.py check <文件路径>")
        print("  python delta-track.py record <文件路径> <哈希> [--l2 路径] [--l3 路径]")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if action == "check":
        sys.exit(check_file(file_path))
    elif action == "record":
        if len(sys.argv) < 4:
            print("错误: record 需要提供内容哈希")
            sys.exit(1)

        content_hash = sys.argv[3]
        l2_pages = None
        l3_pages = None

        # 解析可选参数
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--l2" and i + 1 < len(sys.argv):
                l2_pages = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--l3" and i + 1 < len(sys.argv):
                l3_pages = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        sys.exit(record_ingestion(file_path, content_hash, l2_pages, l3_pages))
    else:
        print(f"未知操作: {action}")
        sys.exit(1)
