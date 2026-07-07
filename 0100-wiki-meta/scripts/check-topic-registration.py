#!/usr/bin/env python3
"""检查 L2 topic 是否已注册到 topics.yaml"""
import sys
import re
import yaml
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parent.parent.parent
TOPICS_FILE = ROOT / "0100-wiki-meta" / "configs" / "topics.yaml"


def load_active_topics() -> Set[str]:
    """加载topics.yaml中的active主题"""
    try:
        cfg = yaml.safe_load(TOPICS_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"[ERROR] 无法加载topics.yaml: {e}")
        sys.exit(1)

    active = set()
    for domain_data in (cfg.get('domains') or {}).values():
        active.update(domain_data.get('active') or [])
    return active


def check_topic_registration() -> List[str]:
    """检查所有L2文件的topic是否已注册"""
    issues = []
    active_topics = load_active_topics()

    # 扫描所有L2文件
    for md in ROOT.rglob("*.md"):
        rel = str(md.relative_to(ROOT)).replace('\\', '/')

        # 跳过非内容目录
        if any(p in rel for p in ['.trash', '.git', '0000-meta', '0100-wiki-meta',
                                    '0003-inbox', '0109-log']):
            continue

        try:
            content = md.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not m:
                continue

            fm = yaml.safe_load(m.group(1)) or {}
            if fm.get('layer') != 'L2':
                continue

            topic = fm.get('topic')
            if topic and topic not in active_topics:
                issues.append(f"{rel}: topic '{topic}' 未注册到 topics.yaml")
        except Exception:
            continue

    return issues


def main():
    """主入口"""
    issues = check_topic_registration()

    if issues:
        print("[WARNING] 发现未注册的topic")
        for issue in issues:
            print(f"  - {issue}")
        print("\n未注册topic需添加到0100-wiki-meta/configs/topics.yaml")
        sys.exit(1)
    else:
        print("[OK] 所有L2 topic已注册")
        sys.exit(0)


if __name__ == "__main__":
    main()
