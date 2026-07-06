#!/usr/bin/env python3
"""check-similarity.py - 标题相似度检测"""
import sys, sqlite3
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_similar_titles(new_title, threshold=0.8):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT path, title FROM notes WHERE layer='L3' AND kind='concept'")

    similar = []
    for path, title in cursor.fetchall():
        ratio = similarity(new_title, title)
        if ratio >= threshold:
            similar.append((title, path, ratio))

    conn.close()
    similar.sort(key=lambda x: x[2], reverse=True)
    return similar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check-similarity.py <标题> [--threshold 0.8]")
        sys.exit(1)

    new_title = sys.argv[1]
    threshold = 0.8
    if len(sys.argv) > 3 and sys.argv[2] == "--threshold":
        threshold = float(sys.argv[3])

    results = check_similar_titles(new_title, threshold)

    if results:
        print(f"⚠️  发现 {len(results)} 个相似标题：")
        for title, path, ratio in results:
            print(f"  {ratio:.2%} - [[{title}]] ({path})")
        sys.exit(1)
    else:
        print(f"✓ 无相似标题（阈值 {threshold}）")
        sys.exit(0)
