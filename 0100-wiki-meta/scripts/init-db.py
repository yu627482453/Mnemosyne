#!/usr/bin/env python3
"""初始化 Mnemosyne 知识库索引数据库"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / ".wiki.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 性能优化 PRAGMA
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.execute("PRAGMA cache_size=-32000")
    cur.execute("PRAGMA temp_store=MEMORY")
    cur.execute("PRAGMA foreign_keys=ON")

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

    # 检查版本并执行迁移
    cur.execute("PRAGMA user_version")
    version = cur.fetchone()[0]

    if version < 1:
        # Delta 跟踪：记录已摄入的源文件
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingested_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL UNIQUE,
                content_hash TEXT NOT NULL,
                ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                status TEXT CHECK(status IN ('active','archived')) DEFAULT 'active'
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ingested_hash ON ingested_files(content_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ingested_status ON ingested_files(status)")

        # 文件产出的页面关联
        cur.execute("""
            CREATE TABLE IF NOT EXISTS file_produces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER NOT NULL,
                produced_page_path TEXT NOT NULL,
                page_layer TEXT NOT NULL CHECK(page_layer IN ('L2','L3')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_file_id) REFERENCES ingested_files(id) ON DELETE CASCADE,
                UNIQUE(source_file_id, produced_page_path)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fp_source ON file_produces(source_file_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fp_page ON file_produces(produced_page_path)")

        # Wikilinks 关系表：记录 [[wikilink]] 引用关系
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wikilinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                target_slug TEXT NOT NULL,
                target_path TEXT,
                link_type TEXT CHECK(link_type IN ('wikilink','planned')) DEFAULT 'wikilink',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_path, target_slug, link_type)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_wl_source ON wikilinks(source_path)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_wl_target ON wikilinks(target_slug)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_wl_dead ON wikilinks(target_path) WHERE target_path IS NULL")

        cur.execute("PRAGMA user_version = 1")

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

if __name__ == "__main__":
    init_db()
