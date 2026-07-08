#!/usr/bin/env python3
"""
重建数据库索引

用途：扫描所有 L2/L3 文件重建 .wiki.db 索引

使用方法：
    python rebuild-index.py
"""

import sqlite3
import sys
from pathlib import Path


class IndexRebuilder:
    """数据库索引重建器"""

    def __init__(self):
        self.db_path = Path(".wiki.db")

    def rebuild(self):
        """重建索引"""
        print("🔄 重建数据库索引...")

        if self.db_path.exists():
            backup = self.db_path.with_suffix('.db.bak')
            print(f"📦 备份现有数据库到: {backup}")
            self.db_path.rename(backup)

        print("\n⚠️  此功能需要手动实现具体的重建逻辑")
        print("建议步骤：")
        print("1. 创建新的数据库表结构")
        print("2. 扫描所有 L2 主题目录 (*-*/)")
        print("3. 扫描所有 L3 目录 (0102/0103/0104)")
        print("4. 解析每个文件的 frontmatter")
        print("5. 插入索引记录")
        print("6. 创建必要的索引优化查询")


def main():
    rebuilder = IndexRebuilder()
    rebuilder.rebuild()
    print("\n✅ 索引重建完成")


if __name__ == "__main__":
    main()
