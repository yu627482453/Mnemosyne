#!/bin/bash
# Mnemosyne Lint Runner — 运行所有可脚本化的检查
echo "=== 1. Content Hash ===" && python3 0100-wiki-meta/scripts/check-content-hash.py . || true
echo "=== 2. Planned Links ===" && python3 0100-wiki-meta/scripts/check-planned-links.py . || true
echo "=== 3. Broken Wikilinks ===" && echo "(manual check — rg '\[\[' + Glob verify)" || true
echo "=== Lint complete ==="
