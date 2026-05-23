"""校验 L2 content_hash 与实际文件内容是否一致"""
import hashlib, sys, re, os

vault_root = sys.argv[1] if len(sys.argv) > 1 else "."
issues = []

for root, dirs, files in os.walk(vault_root):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("0000-meta","0100-wiki-meta","0003-inbox")]
    for f in files:
        if not f.endswith(".md"): continue
        path = os.path.join(root, f)
        with open(path, "rb") as fh:
            content = fh.read()
        actual_hash = hashlib.sha256(content).hexdigest()[:8]
        # Extract frontmatter content_hash
        text = content.decode("utf-8", errors="ignore")
        m = re.search(r"content_hash:\s*\"?([a-f0-9]{8})\"?", text)
        if m and m.group(1) != actual_hash:
            issues.append(f"{path}: expected={m.group(1)} actual={actual_hash}")

if issues:
    print("Content hash mismatch:")
    for i in issues: print(f"  {i}")
    sys.exit(1)
else:
    print("All content_hash checks passed.")
