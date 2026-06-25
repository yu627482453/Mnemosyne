#!/usr/bin/env python3
"""初始化 Mnemosyne 知识库索引数据库"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 启用外键约束
    cur.execute("PRAGMA foreign_keys = ON")

    # 表 1: notes（核心笔记表）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            path TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            layer TEXT NOT NULL CHECK(layer IN ('L1','L2','L3')),
            kind TEXT,
            status TEXT CHECK(status IN ('draft','published')),
            summary TEXT,
            created DATE,
            updated DATE NOT NULL,
            updated_ts INTEGER,
            layer_data TEXT,
            topic TEXT GENERATED ALWAYS AS (json_extract(layer_data, '$.topic')) VIRTUAL,
            processing_path TEXT GENERATED ALWAYS AS (json_extract(layer_data, '$.processing_path')) VIRTUAL,
            FOREIGN KEY (topic) REFERENCES topics(topic_dir) ON DELETE SET NULL
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_layer ON notes(layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_topic ON notes(topic)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_updated_ts ON notes(updated_ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON notes(status)")

    # 表 2: topics（主题词表）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            topic_dir TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            category TEXT,
            range_start INTEGER,
            range_end INTEGER,
            description TEXT,
            created DATE DEFAULT CURRENT_DATE
        )
    """)

    # 表 3: tags（标签词表）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag TEXT PRIMARY KEY,
            tag_en TEXT,
            tag_zh TEXT,
            language TEXT DEFAULT 'en' CHECK(language IN ('en','zh')),
            aliases TEXT,
            category TEXT,
            description TEXT,
            usage_count INTEGER DEFAULT 0,
            created DATE DEFAULT CURRENT_DATE
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tags_language ON tags(language)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tags_usage ON tags(usage_count DESC)")

    # 表 4: note_tags（笔记-标签关系）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS note_tags (
            note_path TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (note_path, tag),
            FOREIGN KEY (note_path) REFERENCES notes(path) ON DELETE CASCADE,
            FOREIGN KEY (tag) REFERENCES tags(tag) ON DELETE CASCADE
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_note_tags_tag ON note_tags(tag)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_note_tags_note ON note_tags(note_path)")

    # 表 5: notes_fts（全文搜索）
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            path UNINDEXED,
            title,
            summary,
            content='notes',
            content_rowid='rowid',
            tokenize='unicode61'
        )
    """)

    # 触发器：自动同步 FTS5
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, path, title, summary)
            VALUES (new.rowid, new.path, new.title, new.summary);
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
