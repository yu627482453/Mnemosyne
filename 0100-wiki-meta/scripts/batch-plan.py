#!/usr/bin/env python3
"""批量并行优化 - 智能文件聚类和并行处理"""
import sys
from pathlib import Path
from typing import List, Set, Dict
import json

WIKI_ROOT = Path(__file__).parent.parent.parent


def parse_wikilinks(md_file: Path) -> Set[str]:
    """提取文件中的wikilink依赖"""
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception:
        return set()

    import re
    links = re.findall(r'\[\[([^\]|#]+)', content)
    return {link.strip() for link in links}


def build_dependency_graph(files: List[Path]) -> Dict[str, Set[str]]:
    """构建文件依赖图"""
    graph = {}
    slug_to_path = {}

    for f in files:
        slug = f.stem
        rel_path = str(f.relative_to(WIKI_ROOT)).replace('\\', '/')
        slug_to_path[slug] = rel_path
        graph[rel_path] = set()

    for f in files:
        rel_path = str(f.relative_to(WIKI_ROOT)).replace('\\', '/')
        wikilinks = parse_wikilinks(f)

        for link in wikilinks:
            if link in slug_to_path:
                target = slug_to_path[link]
                if target != rel_path:
                    graph[rel_path].add(target)

    return graph


def topological_sort(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """拓扑排序，返回分层的文件组（同层可并行）"""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[dep] += 1

    layers = []
    remaining = set(graph.keys())

    while remaining:
        current_layer = [n for n in remaining if in_degree[n] == 0]
        if not current_layer:
            current_layer = list(remaining)

        layers.append(current_layer)

        for node in current_layer:
            remaining.remove(node)
            for neighbor in graph:
                if node in graph[neighbor] and neighbor in remaining:
                    in_degree[neighbor] -= 1

    return layers


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="批量并行处理规划")
    parser.add_argument('--pattern', type=str, default='**/*.md',
                       help='文件匹配模式')
    parser.add_argument('--output', type=str,
                       help='输出计划到JSON文件')
    args = parser.parse_args()

    files = list(WIKI_ROOT.glob(args.pattern))
    files = [f for f in files if f.is_file()
             and '.trash' not in str(f)
             and '.git' not in str(f)]

    print(f"发现 {len(files)} 个文件")

    graph = build_dependency_graph(files)
    layers = topological_sort(graph)

    print(f"\n生成 {len(layers)} 个并行批次：")
    for i, layer in enumerate(layers, 1):
        print(f"  批次 {i}: {len(layer)} 个文件（可并行）")

    if args.output:
        plan = {
            'total_files': len(files),
            'total_layers': len(layers),
            'layers': [
                {'batch': i+1, 'size': len(layer), 'files': layer}
                for i, layer in enumerate(layers)
            ]
        }
        Path(args.output).write_text(json.dumps(plan, indent=2, ensure_ascii=False))
        print(f"\n计划已保存到 {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
