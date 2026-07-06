#!/usr/bin/env python3
"""check-similarity.py - 标题相似度检测"""
import sys, sqlite3
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_similar_titles(new_title, threshold=0.75):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    similar = []

    # 通道 1：字符串相似度（阈值降至 0.75）
    cursor.execute("SELECT path, title FROM notes WHERE layer='L3' AND kind='concept'")
    for path, title in cursor.fetchall():
        ratio = similarity(new_title, title)
        if ratio >= threshold:
            similar.append((title, path, ratio, 'string'))

    # 通道 2：FTS5 BM25（语义近似补充）
    keywords = ' OR '.join(w for w in new_title.split() if len(w) > 1)
    if keywords:
        try:
            cursor.execute("""
                SELECT n.path, n.title, bm25(notes_fts) AS score
                FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
                WHERE notes_fts MATCH ? AND n.layer='L3' AND n.kind='concept'
                ORDER BY score LIMIT 5
            """, (keywords,))
            for path, title, _ in cursor.fetchall():
                if not any(s[1] == path for s in similar):
                    similar.append((title, path, 0.7, 'fts'))
        except Exception:
            pass

    conn.close()
    similar.sort(key=lambda x: x[2], reverse=True)
    return similar

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check-similarity.py <标题> [--threshold 0.8]")
        sys.exit(1)

    new_title = sys.argv[1]
    threshold = 0.75
    if len(sys.argv) > 3 and sys.argv[2] == "--threshold":
        threshold = float(sys.argv[3])

    results = check_similar_titles(new_title, threshold)

    if results:
        print(f"⚠️  发现 {len(results)} 个相似标题：")
        for title, path, ratio, method in results:
            method_label = "字符匹配" if method == 'string' else "语义相关"
            print(f"  {ratio:.2%} ({method_label}) - [[{title}]] ({path})")
        sys.exit(1)
    else:
        print(f"✓ 无相似标题（阈值 {threshold}）")
        sys.exit(0)
