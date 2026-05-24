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
        source = fm.get("source", "")
        if source and not isinstance(source, str):
            pass
        elif source and source.startswith("http"):
            issues.append(f"source 是 URL '{source}'，应填枚举值 url，实际URL放入source_url")
        tags = fm.get("tags", [])
        if len(tags) < 5:
            issues.append(f"tags 只有 {len(tags)} 个，需要 ≥5")
        status = fm.get("status", "")
        if status not in ("draft", "published"):
            issues.append(f"status '{status}' 应为 draft 或 published")
    # L3 checks
    if layer == "L3":
        pp = fm.get("processing_path", "")
        if not re.match(r"^\S+/\S+$", str(pp)):
            issues.append(f"processing_path '{pp}' 应为 '大类/主题域' 格式")
        tags = fm.get("tags", [])
        if len(tags) < 5:
            issues.append(f"tags 只有 {len(tags)} 个，需要 ≥5")

    if issues:
        print(f"[VALIDATE] {path}:")
        for i in issues: print(f"  ⚠ {i}")
    else:
        print(f"[VALIDATE] {path}: OK")
except Exception as e:
    print(f"[VALIDATE] {path}: error - {e}")
