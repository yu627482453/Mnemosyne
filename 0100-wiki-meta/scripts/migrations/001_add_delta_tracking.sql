-- Delta 跟踪表：记录已摄入的文件
CREATE TABLE IF NOT EXISTS ingested_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL UNIQUE,
    content_hash TEXT NOT NULL,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    status TEXT CHECK(status IN ('active','archived')) DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_ingested_files_hash ON ingested_files(content_hash);
CREATE INDEX IF NOT EXISTS idx_ingested_files_status ON ingested_files(status);

-- 文件产出的页面关联表
CREATE TABLE IF NOT EXISTS file_produces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_id INTEGER NOT NULL,
    produced_page_path TEXT NOT NULL,
    page_layer TEXT NOT NULL CHECK(page_layer IN ('L2','L3')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_file_id) REFERENCES ingested_files(id) ON DELETE CASCADE,
    UNIQUE(source_file_id, produced_page_path)
);

CREATE INDEX IF NOT EXISTS idx_file_produces_source ON file_produces(source_file_id);
CREATE INDEX IF NOT EXISTS idx_file_produces_page ON file_produces(produced_page_path);
