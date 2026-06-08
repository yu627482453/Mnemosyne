"""校验 L2 content_hash 与实际正文内容是否一致（仅 frontmatter 之后的正文部分）"""
import hashlib, sys, re, os

vault_root = sys.argv[1] if len(sys.argv) > 1 else "."
issues = []

for root, dirs, files in os.walk(vault_root):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("0000-meta","0100-wiki-meta","0003-inbox","0109-log")]
    for f in files:
        if not f.endswith(".md"): continue
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
        body = parts[2] if len(parts) >= 3 else content
        actual_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]
        m = re.search(r"content_hash:\s*\"?([a-f0-9]{8})\"?", content)
        if m and m.group(1) != actual_hash:
            issues.append(f"{path}: expected={m.group(1)} actual={actual_hash}")

if issues:
    print("Content hash mismatch:")
    for i in issues: print(f"  {i}")
    sys.exit(1)
else:
    print("All content_hash checks passed.")
