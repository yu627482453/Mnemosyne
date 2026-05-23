"""检查 L2 wikilink 中是否存在未创建的页面"""
import os, re, sys

vault_root = sys.argv[1] if len(sys.argv) > 1 else "."
all_pages = set()

# Collect all existing .md files (by slug/filename)
for root, dirs, files in os.walk(vault_root):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for f in files:
        if f.endswith(".md"):
            all_pages.add(os.path.splitext(f)[0])

# Check wikilinks
for root, dirs, files in os.walk(vault_root):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for f in files:
        if not f.endswith(".md"): continue
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        # Find wikilinks: [[target]] or [[path/target|label]]
        links = re.findall(r"\[\[([^\]|#]+)", content)
        for link in links:
            target = link.split("/")[-1]  # Get slug/filename part
            target = target.split(".")[0] if "." in target else target
            if target not in all_pages and not target.startswith("0001-"):
                print(f"  {path}: [[{link}]] → missing")

print("Done.")
