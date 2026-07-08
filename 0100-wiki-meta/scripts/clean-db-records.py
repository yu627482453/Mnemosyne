#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理数据库中的文件记录

用途：从 .wiki.db 删除指定文件的索引记录

使用方法：
    python clean-db-records.py --files "3000-Agent/file.md"
    python clean-db-records.py --batch-id 20260708_011658
"""

import argparse
import sqlite3
import sys
import io
from pathlib import Path

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DatabaseCleaner:
    """数据库记录清理器"""

    def __init__(self, db_path: str = ".wiki.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            print(f"❌ 数据库不存在: {self.db_path}")
            sys.exit(1)

    def clean_files(self, file_paths: list) -> int:
        """删除指定文件的记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        deleted = 0
        for path in file_paths:
            cursor.execute("DELETE FROM notes WHERE path = ?", (path,))
            if cursor.rowcount > 0:
                print(f"✓ 删除: {path}")
                deleted += cursor.rowcount
        conn.commit()
        conn.close()
        return deleted

    def clean_batch(self, batch_id: str) -> int:
        """根据批次 ID 清理记录"""
        manifest_path = Path(f".trash/remove-l2-{batch_id}/manifest.txt")
        if not manifest_path.exists():
            print(f"❌ 批次清单不存在: {manifest_path}")
            return 0

        # 解析 manifest 获取文件列表
        files = []
        with open(manifest_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('l2_file:'):
                    files.append(line.split(':', 1)[1].strip())

        return self.clean_files(files) if files else 0


def main():
    parser = argparse.ArgumentParser(description='清理数据库记录')
    parser.add_argument('--files', nargs='+', help='要清理的文件路径列表')
    parser.add_argument('--batch-id', help='删除批次 ID')
    parser.add_argument('--db', default='.wiki.db', help='数据库路径')
    args = parser.parse_args()

    if not args.files and not args.batch_id:
        print("❌ 请指定 --files 或 --batch-id")
        sys.exit(1)

    cleaner = DatabaseCleaner(args.db)

    if args.batch_id:
        deleted = cleaner.clean_batch(args.batch_id)
    else:
        deleted = cleaner.clean_files(args.files)

    print(f"\n✅ 共删除 {deleted} 条记录")


if __name__ == "__main__":
    main()
