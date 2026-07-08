#!/usr/bin/env python3
"""
定期清理超过指定天数的 .trash/ 内容

用途：自动清理超过 N 天的删除批次，释放磁盘空间

使用方法：
    python clean-old-trash.py --days 30
    python clean-old-trash.py --days 30 --dry-run
"""

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


class TrashCleaner:
    """垃圾回收站清理器"""

    def __init__(self, days: int, dry_run: bool = False):
        self.days = days
        self.dry_run = dry_run
        self.trash_root = Path(".trash")
        self.cutoff_date = datetime.now() - timedelta(days=days)

    def find_old_batches(self):
        """查找超过指定天数的批次"""
        old_batches = []
        if not self.trash_root.exists():
            return old_batches

        for batch_dir in self.trash_root.glob("remove-l2-*"):
            if batch_dir.is_dir():
                mtime = datetime.fromtimestamp(batch_dir.stat().st_mtime)
                if mtime < self.cutoff_date:
                    old_batches.append((batch_dir, mtime))

        return sorted(old_batches, key=lambda x: x[1])

    def clean(self):
        """执行清理"""
        old_batches = self.find_old_batches()

        if not old_batches:
            print(f"✅ 没有超过 {self.days} 天的批次需要清理")
            return

        print(f"📋 找到 {len(old_batches)} 个超过 {self.days} 天的批次")
        print()

        total_size = 0
        for batch_dir, mtime in old_batches:
            size = sum(f.stat().st_size for f in batch_dir.rglob('*') if f.is_file())
            age_days = (datetime.now() - mtime).days
            print(f"  {batch_dir.name}")
            print(f"    创建时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    距今: {age_days} 天")
            print(f"    大小: {size / 1024 / 1024:.2f} MB")
            total_size += size

        print(f"\n总计: {total_size / 1024 / 1024:.2f} MB")

        if self.dry_run:
            print("\n🔍 模拟模式，不会实际删除")
            return

        print("\n⚠️  即将永久删除以上批次，此操作不可恢复！")
        confirm = input("确认删除？(yes/N): ")
        if confirm.lower() != 'yes':
            print("❌ 已取消")
            return

        for batch_dir, _ in old_batches:
            shutil.rmtree(batch_dir)
            print(f"✓ 已删除: {batch_dir.name}")

        print(f"\n✅ 清理完成，释放 {total_size / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser(description='清理超过指定天数的 .trash/ 批次')
    parser.add_argument('--days', type=int, default=30, help='清理超过多少天的批次（默认30天）')
    parser.add_argument('--dry-run', action='store_true', help='模拟模式，仅查看不删除')
    args = parser.parse_args()

    cleaner = TrashCleaner(args.days, args.dry_run)
    cleaner.clean()


if __name__ == "__main__":
    main()
