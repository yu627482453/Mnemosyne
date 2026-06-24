"""PostToolUse hook: validate frontmatter of written .md files against schema.yaml"""
import sys, os, re, yaml

path = sys.argv[1] if len(sys.argv) > 1 else ""
if not path.endswith(".md"): sys.exit(0)
# Skip non-knowledge files
if "0000-meta" in path or "0100-wiki-meta" in path or ".trash" in path: sys.exit(0)

try:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m: sys.exit(0)  # No frontmatter
    fm = yaml.safe_load(m.group(1))
    if not fm: sys.exit(0)
    layer = fm.get("layer", "")

    issues = []
    # L2 checks
    if layer == "L2":
        topic = fm.get("topic", "")
        if not re.match(r"^\d{4}-.+$", str(topic)):
            issues.append(f"topic '{topic}' 不匹配 '####-name' 格式")
        if not fm.get("id"):
            issues.append("id 字段缺失")
        kind = fm.get("kind", "")
        if kind != "standard":
            issues.append(f"kind '{kind}' 应为 standard")
        if not fm.get("created"):
            issues.append("created 字段缺失")
        source = fm.get("source", "")
        if not source:
            issues.append("source 字段缺失")
        elif source and not isinstance(source, str):
            pass
        elif source and source.startswith("http"):
            issues.append(f"source 是 URL '{source}'，应填枚举值 url，实际URL放入source_url")
        elif source not in ("manual", "url", "file", "claude"):
            issues.append(f"source '{source}' 不在枚举值 [manual, url, file, claude]")
        aliases = fm.get("aliases", [])
        if not aliases or len(aliases) < 1:
            issues.append("aliases 字段缺失或为空")
        tags = fm.get("tags", [])
        if len(tags) < 5:
            issues.append(f"tags 只有 {len(tags)} 个，需要 ≥5")
        if len(tags) > 10:
            issues.append(f"tags 有 {len(tags)} 个，需要 ≤10")
        status = fm.get("status", "")
        if status not in ("draft", "published"):
            issues.append(f"status '{status}' 应为 draft 或 published")
        summary = fm.get("summary", "")
        if not summary:
            issues.append("summary 字段缺失")
        else:
            slen = len(str(summary))
            if slen < 200:
                issues.append(f"summary 只有 {slen} 字，需要 ≥200")
            elif slen > 500:
                issues.append(f"summary 有 {slen} 字，需要 ≤500")
    # L3 checks
    if layer == "L3":
        pp = fm.get("processing_path", "")
        if not pp or not re.match(r"^\S+/\S+$", str(pp)):
            issues.append(f"processing_path '{pp}' 应为 '大类/主题域' 格式")
        tags = fm.get("tags", [])
        if len(tags) < 5:
            issues.append(f"tags 只有 {len(tags)} 个，需要 ≥5")
        if len(tags) > 10:
            issues.append(f"tags 有 {len(tags)} 个，需要 ≤10")
        summary = fm.get("summary", "")
        if not summary:
            issues.append("summary 字段缺失")
        else:
            slen = len(str(summary))
            if slen < 200:
                issues.append(f"summary 只有 {slen} 字，需要 ≥200")
            elif slen > 500:
                issues.append(f"summary 有 {slen} 字，需要 ≤500")
        kind = fm.get("kind", "")
        if kind not in ("topic", "concept", "entity", "comparison"):
            issues.append(f"kind '{kind}' 不在枚举值 [topic, concept, entity, comparison]")
        if kind == "entity" and not fm.get("entity_type"):
            issues.append("kind=entity 但缺少 entity_type")
        if kind == "comparison":
            if not fm.get("comparison_axis"):
                issues.append("kind=comparison 但缺少 comparison_axis")
            if not fm.get("lhs"):
                issues.append("kind=comparison 但缺少 lhs")
            if not fm.get("rhs"):
                issues.append("kind=comparison 但缺少 rhs")

    if issues:
        print(f"[VALIDATE] {path}:")
        for i in issues: print(f"  ⚠ {i}")
    else:
        print(f"[VALIDATE] {path}: OK")
except Exception as e:
    print(f"[VALIDATE] {path}: error - {e}")
