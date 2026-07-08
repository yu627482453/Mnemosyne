#!/usr/bin/env python3
"""
检查删除操作的完成状态

用途：识别中断的删除批次、验证完整性、提供恢复建议

使用方法：
    python check-remove-status.py --batch-id 20260708_011658
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class RemoveStatusChecker:
    """删除状态检查器"""

    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.trash_dir = Path(f".trash/remove-l2-{batch_id}")
        self.manifest_path = self.trash_dir / "manifest.txt"

    def check_batch_exists(self) -> bool:
        """检查批次是否存在"""
        return self.trash_dir.exists()

    def parse_manifest(self) -> Dict:
        """解析删除清单"""
        if not self.manifest_path.exists():
            return {}

        manifest = {}
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    manifest[key.strip()] = value.strip()
        return manifest

    def check_files_in_trash(self) -> Tuple[List[Path], List[Path], List[Path]]:
        """检查 .trash/ 中的文件"""
        l2_files = list((self.trash_dir / "l2").glob("*.md")) if (self.trash_dir / "l2").exists() else []
        l3_files = list((self.trash_dir / "l3").glob("*.md")) if (self.trash_dir / "l3").exists() else []
        resources = list((self.trash_dir / "resources").rglob("*.*")) if (self.trash_dir / "resources").exists() else []
        return l2_files, l3_files, resources

    def check_log_exists(self) -> bool:
        """检查操作日志是否存在"""
        log_path = Path(f"0109-log/remove-l2-{self.batch_id}.md")
        return log_path.exists()

    def analyze_status(self) -> str:
        """分析删除状态"""
        if not self.check_batch_exists():
            return "NOT_FOUND"

        manifest = self.parse_manifest()
        l2_files, l3_files, resources = self.check_files_in_trash()
        log_exists = self.check_log_exists()

        # 判断完成状态
        expected_l3 = int(manifest.get('l3_count', 0))
        expected_res = int(manifest.get('resource_count', 0))

        if len(l2_files) == 0:
            return "INCOMPLETE"  # L2 未移动

        if len(l3_files) < expected_l3 or len(resources) < expected_res:
            return "PARTIAL"  # 部分完成

        if not log_exists:
            return "NO_LOG"  # 文件已删除但日志缺失

        return "COMPLETED"

    def generate_report(self) -> str:
        """生成状态报告"""
        status = self.analyze_status()
        manifest = self.parse_manifest()
        l2_files, l3_files, resources = self.check_files_in_trash()

        report = []
        report.append(f"批次 ID: {self.batch_id}")
        report.append(f"状态: {status}")
        report.append("=" * 60)

        if status == "NOT_FOUND":
            report.append("❌ 批次不存在")
            return "\n".join(report)

        report.append(f"\n【清单信息】")
        report.append(f"时间戳: {manifest.get('timestamp', 'N/A')}")
        report.append(f"L2 文件: {manifest.get('l2_file', 'N/A')}")
        report.append(f"预期 L3: {manifest.get('l3_count', 0)} 个")
        report.append(f"预期资源: {manifest.get('resource_count', 0)} 个")

        report.append(f"\n【实际状态】")
        report.append(f"L2 文件: {len(l2_files)} 个")
        report.append(f"L3 文件: {len(l3_files)} 个")
        report.append(f"资源文件: {len(resources)} 个")

        log_exists = self.check_log_exists()
        report.append(f"操作日志: {'✓ 存在' if log_exists else '✗ 缺失'}")

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='检查删除操作的完成状态')
    parser.add_argument('--batch-id', required=True, help='删除批次 ID')
    args = parser.parse_args()

    checker = RemoveStatusChecker(args.batch_id)
    report = checker.generate_report()
    print(report)

    status = checker.analyze_status()
    if status == "COMPLETED":
        print("\n✅ 删除操作已完成")
        sys.exit(0)
    elif status == "PARTIAL":
        print("\n⚠️  删除操作未完成，可使用 resume-remove.py 继续")
        sys.exit(1)
    elif status == "INCOMPLETE":
        print("\n❌ 删除操作中断，可使用 rollback-remove.py 回滚")
        sys.exit(2)
    elif status == "NO_LOG":
        print("\n⚠️  文件已删除但日志缺失")
        sys.exit(1)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()

