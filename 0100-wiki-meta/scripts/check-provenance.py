#!/usr/bin/env python3
"""检查置信度和来源标注完整性"""
import sys
import re
import yaml
from pathlib import Path
from typing import List

WIKI_ROOT = Path(__file__).parent.parent.parent


def check_provenance(md_file: Path) -> List[str]:
    """检查confidence和provenance字段完整性"""
    issues = []

    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        return [f"无法读取文件: {e}"]

    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        return [f"frontmatter解析失败: {e}"]

    # 检查confidence字段
    conf = fm.get('confidence')
    if conf is None:
        issues.append("缺少confidence字段")
    elif not isinstance(conf, (int, float)):
        issues.append(f"confidence类型错误: {type(conf).__name__}")
    elif not (0.0 <= conf <= 1.0):
        issues.append(f"confidence超出范围: {conf}")

    # 检查provenance字段
    prov = fm.get('provenance')
    if prov is None:
        issues.append("缺少provenance字段")
    elif not isinstance(prov, dict):
        issues.append(f"provenance类型错误: {type(prov).__name__}")
    else:
        # 检查比例和
        total = prov.get('extracted', 0) + prov.get('inferred', 0) + prov.get('ambiguous', 0)
        # 容差±0.15（考虑四舍五入和估算误差）
        if abs(total - 1.0) > 0.15:
            issues.append(f"provenance比例和不为1.0（当前{total:.2f}，容差±0.15）")

        # 各比例范围检查
        for key in ['extracted', 'inferred', 'ambiguous']:
            val = prov.get(key, 0)
            if not isinstance(val, (int, float)):
                issues.append(f"provenance.{key}类型错误: {type(val).__name__}")
            elif not (0 <= val <= 1):
                issues.append(f"provenance.{key}超出[0,1]范围: {val}")

    # 检查正文标记数量是否与provenance匹配
    if prov and isinstance(prov, dict):
        body = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        inferred_count = len(re.findall(r'\^\[inferred\]', body))
        ambiguous_count = len(re.findall(r'\^\[ambiguous\]', body))

        # 估算正文总句子数（简单方法：按句号、问号、感叹号分割）
        sentences = len(re.findall(r'[。！？.!?]+', body))
        if sentences == 0:
            sentences = 1  # 避免除零

        inferred_ratio = inferred_count / sentences
        ambiguous_ratio = ambiguous_count / sentences

        # 前向检查：如果provenance显示inferred>30%但标记占比<10%，可能遗漏标记
        if prov.get('inferred', 0) > 0.3 and inferred_ratio < 0.1:
            issues.append(
                f"provenance显示inferred={prov.get('inferred'):.0%}，"
                f"但正文仅{inferred_count}处^[inferred]标记（占比{inferred_ratio:.0%}）"
            )

        # 反向检查：如果标记很多但provenance比例很低，可能估算不准
        if inferred_ratio > 0.3 and prov.get('inferred', 0) < 0.2:
            issues.append(
                f"正文有{inferred_count}处^[inferred]标记（占比{inferred_ratio:.0%}），"
                f"但provenance显示inferred仅{prov.get('inferred'):.0%}"
            )

    return issues


def main():
    """扫描所有L2/L3文件并检查置信度和来源标注"""
    has_issues = False

    for md_file in WIKI_ROOT.rglob("*.md"):
        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')

        # 跳过非内容目录
        if any(p in rel_path for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta',
                                         '0003-inbox', '0109-log']):
            continue

        # 检查是否是L2/L3文件
        try:
            text = md_file.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not m:
                continue

            fm = yaml.safe_load(m.group(1)) or {}
            layer = fm.get('layer', '')
            if layer not in ('L2', 'L3'):
                continue
        except Exception:
            continue

        # 执行provenance检查
        issues = check_provenance(md_file)
        if issues:
            has_issues = True
            print(f"[WARNING] {rel_path}")
            for issue in issues:
                print(f"  - {issue}")

    if has_issues:
        print("\n发现置信度和来源标注问题（WARNING级别）")
        sys.exit(1)
    else:
        print("[OK] 所有置信度和来源标注完整")
        sys.exit(0)


if __name__ == "__main__":
    main()
