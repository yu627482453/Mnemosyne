#!/usr/bin/env python3
"""初始化 Mnemosyne 知识库索引数据库"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            path TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            layer TEXT CHECK(layer IN ('L1','L2','L3')),
            kind TEXT,
            topic TEXT,
            tags TEXT,
            summary TEXT,
            created DATE,
            updated DATE
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_layer ON notes(layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_topic ON notes(topic)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_updated ON notes(updated DESC)")

    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            title, summary, content='notes', content_rowid='rowid'
        )
    """)

    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, title, summary)
            VALUES (new.rowid, new.title, new.summary);
        END
    """)

    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            DELETE FROM notes_fts WHERE rowid = old.rowid;
        END
    """)

    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            UPDATE notes_fts SET title = new.title, summary = new.summary
            WHERE rowid = new.rowid;
        END
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

if __name__ == "__main__":
    init_db()
