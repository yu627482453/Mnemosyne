# Mnemosyne 优化规格说明书

> 基于 D:\obsidian（当前工程）与 D:\gitRepository\obsidian-wiki（参考工程）对比分析
> 版本：v1.0 | 日期：2026-07-06 | 状态：待审查

---

## 背景与目标

本 spec 梳理当前 Mnemosyne 工程（D:\obsidian）相较于参考实现（obsidian-wiki）在设计约束、skill 规范、脚本实现上的差距，并针对 SQLite 数据层提出系统性增强方案。

**优化目标**：
- 消除运行时 Bug（ingested_files 表缺失等致命问题）
- 提升索引性能（增量更新替代全量重建）
- 补全缺失功能（wikilinks 表、lint 覆盖、hot.md 管理）
- 统一规范一致性（图片命名、title 提取、条目上限）

---

## 问题全景

| 域 | 问题数 | 最高严重度 |
|---|---|---|
| SQLite 数据层 | 8 项 | 🔴 致命 |
| 设计约束一致性 | 6 项 | 🔴 高 |
| Skill / 工具链 | 5 项 | 🟡 中 |

---

## 第一部分：SQLite 数据层优化

### SQLITE-01 🔴 致命：`ingested_files` 表缺失

**文件**：`0100-wiki-meta/scripts/delta-track.py:16`、`init-db.py`

**问题描述**：`delta-track.py` 查询 `ingested_files` 和 `file_produces` 表，但 `init-db.py` 从未创建这两张表。`migrations/001_add_delta_tracking.sql` 是孤立文件，无任何脚本自动执行，导致 `delta-track.py check` 和 `record` 命令运行时直接报 `OperationalError: no such table`。

**根因**：迁移文件未与 `init-db.py` 集成，缺少 schema 版本控制机制。

**修复方案**：将两张表合并进 `init-db.py`，引入 `PRAGMA user_version` 做版本门控。

```python
# init-db.py — 在 conn.commit() 之前添加以下内容

cur.execute("PRAGMA user_version")
version = cur.fetchone()[0]

if version < 1:
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
    cur.execute("PRAGMA user_version = 1")
```

**验收**：`sqlite3 .wiki.db ".tables"` 应包含 `ingested_files` 和 `file_produces`；`delta-track.py check <文件>` 不抛异常。

---

### SQLITE-02 🔴 高：全量重建索引，FTS 性能差

**文件**：`0100-wiki-meta/scripts/index-notes.py:67-70`

**问题描述**：每次运行都 `DELETE FROM notes`，触发 FTS5 触发器逐行删除再逐行插入。百条笔记以上时耗时显著增加。

**修复方案 A（推荐）— 增量 upsert**：以 `updated` 字段作为变更信号，跳过未修改文件；清理已删除文件的 DB 条目。

```python
def index_notes_incremental():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # 获取当前索引状态
    cur.execute("SELECT path, updated FROM notes")
    indexed = {row[0]: str(row[1]) for row in cur.fetchall()}

    added = updated_count = deleted = 0
    current_paths = set()

    for md_file in WIKI_ROOT.rglob("*.md"):
        # ... 过滤 + 解析 frontmatter（同原逻辑）...
        rel_path = str(md_file.relative_to(WIKI_ROOT)).replace('\\', '/')
        current_paths.add(rel_path)
        file_updated = str(meta.get('updated', ''))

        if rel_path in indexed and indexed[rel_path] == file_updated:
            continue  # 未变更，跳过

        cur.execute("INSERT OR REPLACE INTO notes (...) VALUES (...)", (...))
        updated_count += 1 if rel_path in indexed else (added := added + 1) or 0

    # 清理已删除文件的过期索引
    for path in set(indexed.keys()) - current_paths:
        cur.execute("DELETE FROM notes WHERE path = ?", (path,))
        deleted += 1

    conn.commit()
    print(f"索引完成：新增 {added}，更新 {updated_count}，删除 {deleted}")
```

**修复方案 B — 全量重建时跳过触发器**（用于 `--full-rebuild` 参数）：

```python
cur.execute("DELETE FROM notes_fts")                              # 直接清空 FTS
cur.executemany("INSERT INTO notes (...) VALUES (...)", rows)     # 批量插入
cur.execute("INSERT INTO notes_fts(notes_fts) VALUES('rebuild')") # FTS5 重建
```

**验收**：第二次运行（无变更时）输出 `新增 0，更新 0，删除 0`，耗时 < 1s。

---

### SQLITE-03 🟡 中：缺少 PRAGMA 性能配置

**文件**：`init-db.py` 及所有调用 `sqlite3.connect()` 的脚本

**问题描述**：未设置任何 PRAGMA，Windows 下默认 DELETE journal mode，每次写入都 fsync，批量索引时 I/O 瓶颈明显。

**修复**：`init_db()` 开头及所有连接处统一添加：

```python
# init-db.py 连接后立即执行
cur.execute("PRAGMA journal_mode=WAL")
cur.execute("PRAGMA synchronous=NORMAL")
cur.execute("PRAGMA cache_size=-32000")   # 32MB 内存缓存
cur.execute("PRAGMA temp_store=MEMORY")
cur.execute("PRAGMA foreign_keys=ON")

# 其他脚本（delta-track.py、query.py、check-similarity.py 等）
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")
```

---

### SQLITE-04 🟡 中：`updated_ts` 语义错误

**文件**：`index-notes.py:127`

**问题描述**：`updated_ts` 存的是**索引执行时刻**（`datetime.now().timestamp()`），不是笔记的实际更新时间，导致按"最近更新"排序结果不正确。

**修复**：

```python
updated_str = str(meta.get('updated', ''))
try:
    updated_ts = int(datetime.strptime(updated_str, '%Y-%m-%d').timestamp())
except (ValueError, TypeError):
    updated_ts = 0
```

---

### SQLITE-05 🟡 中：相似度检测精度低

**文件**：`0100-wiki-meta/scripts/check-similarity.py`

**问题描述**：`difflib.SequenceMatcher` 字符级匹配，无法识别"Agent 循环"与"代理循环"等同义中文概念（相似度 < 0.4）。

**修复**：增加 FTS5 BM25 作为语义补充通道，降低字符匹配阈值至 0.75：

```python
def check_similar_titles(new_title, threshold=0.75):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    similar = []

    # 通道 1：字符串相似度
    cur.execute("SELECT path, title FROM notes WHERE layer='L3' AND kind='concept'")
    for path, title in cur.fetchall():
        ratio = similarity(new_title, title)
        if ratio >= threshold:
            similar.append((title, path, ratio, 'string'))

    # 通道 2：FTS5 BM25（语义近似补充）
    keywords = ' OR '.join(w for w in new_title.split() if len(w) > 1)
    if keywords:
        try:
            cur.execute("""
                SELECT n.path, n.title, bm25(notes_fts) AS score
                FROM notes_fts f JOIN notes n ON f.rowid = n.rowid
                WHERE notes_fts MATCH ? AND n.layer='L3' AND n.kind='concept'
                ORDER BY score LIMIT 5
            """, (keywords,))
            for path, title, _ in cur.fetchall():
                if not any(s[1] == path for s in similar):
                    similar.append((title, path, 0.7, 'fts'))
        except Exception:
            pass

    conn.close()
    return sorted(similar, key=lambda x: x[2], reverse=True)
```

---

### SQLITE-06 🟡 中：缺少 wikilinks 关系表

**文件**：`init-db.py`（新增）

**问题描述**：无 wikilinks 表，无法支持反向链接查询、死链批量检测、god nodes 分析，这些功能全依赖 `rg` 扫描，在大型 vault 中性能差。

**新增表（加入 version < 1 迁移块或独立 version 2 块）**：

```sql
CREATE TABLE IF NOT EXISTS wikilinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    target_slug TEXT NOT NULL,
    target_path TEXT,                 -- NULL = 死链
    link_type TEXT CHECK(link_type IN ('wikilink','planned')) DEFAULT 'wikilink',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_path, target_slug, link_type)
);

CREATE INDEX IF NOT EXISTS idx_wl_source ON wikilinks(source_path);
CREATE INDEX IF NOT EXISTS idx_wl_target ON wikilinks(target_slug);
CREATE INDEX IF NOT EXISTS idx_wl_dead   ON wikilinks(target_path) WHERE target_path IS NULL;
```

`index-notes.py` 在索引每个文件时同步提取正文 `[[wikilink]]` 填充此表，解析 `target_path`。

**启用的查询能力**：

```sql
-- 反向链接
SELECT source_path FROM wikilinks WHERE target_slug = 'agent-loop';

-- 死链列表
SELECT source_path, target_slug FROM wikilinks WHERE target_path IS NULL;

-- God Nodes（入链 Top 10）
SELECT target_slug, COUNT(*) AS cnt FROM wikilinks
WHERE link_type='wikilink' GROUP BY target_slug ORDER BY cnt DESC LIMIT 10;
```

---

### SQLITE-07 🟡 中：`check-config-sync.py` 缺少反向清理检查

**文件**：`check-config-sync.py:93-107`（8d 检查）

**问题描述**：只验证"笔记是否在 DB 中"（正向覆盖），不检查"DB 中是否有已删除文件的过期条目"（反向清理）。

**补充代码**：

```python
# 8d 补充：DB 过期条目检查
file_paths = {n.get('_path') for n in notes}
for indexed_path in indexed_paths:
    if indexed_path not in file_paths:
        err("stale_index",
            f"DB 中存在过期条目：{indexed_path}（文件已删除，请重新运行 index-notes.py）")
```

---

### SQLITE-08 🟢 低：`query.py` 功能单一，缺少过滤参数

**文件**：`query.py`

**问题描述**：只支持全文关键词搜索，不支持按 layer/kind/topic/status 过滤。

**增强 CLI 参数**：

```
python query.py "Agent" --layer L3 --kind concept --topic 3000-Agent
python query.py --list-topics                   # 列出所有 active topic
python query.py --backlinks agent-loop          # 反向链接（依赖 SQLITE-06）
python query.py --dead-links                    # 死链报告
python query.py --stats                         # 知识库统计摘要
```

---

## 第二部分：设计约束与规范一致性

### DESIGN-01 🔴 高：图片路径命名规范冲突

**涉及文件**：`CLAUDE.md`（命名规范章节）、`skill-ingest.md:182`（步骤 2 示例）

**问题描述**：CLAUDE.md 规定图片命名为 `{slug}-{timestamp}.{ext}`（时间戳格式），但 `skill-ingest.md` 步骤 2 示例用序号格式 `agent-loop-01.png`，Claude 执行时行为不确定。

**修复**：统一 `skill-ingest.md` 步骤 2 示例：

```
# 正确（时间戳格式）
0001-resource/3000-Agent/agent-loop-20260625143022.png

# 废弃（序号格式，删除示例）
0001-resource/3000-Agent/agent-loop-01.png
```

---

### DESIGN-02 🟡 中：`run-lint.sh` 覆盖率严重不足

**文件**：`run-lint.sh`

**问题描述**：CLAUDE.md 定义了 10+ 项 Lint 检查，脚本只执行 2 项，其余均为 `(manual check)`。

**目标覆盖表**：

| # | 检查项 | 当前状态 | 目标方式 |
|---|---|---|---|
| 1 | content_hash 一致性 | ✅ 脚本 | 保留 |
| 2 | planned_links 残留 | ✅ 脚本 | 保留 |
| 3 | Frontmatter 完整性 | ✅ PostHook | 集成进 lint |
| 4 | 死链（broken wikilink）| ❌ 手动 | DB 查询（依赖 SQLITE-06）|
| 5 | summary < 200 字 | ❌ 未脚本化 | DB 查询 |
| 6 | draft > 30 天 | ❌ 未脚本化 | DB 查询 |
| 7 | topic 未注册 | ❌ 未脚本化 | check-config-sync 补充 |
| 8 | 孤立页面（零反链）| ❌ 未脚本化 | DB 查询（依赖 SQLITE-06）|
| 9 | 远程图片残留 | ❌ 未脚本化 | rg `https?://` in resource_refs |
| 10 | L3 source 失效 | ❌ 未脚本化 | 验证 source 路径存在 |

新增 `check-db-health.py` 脚本，整合 4-8 项基于 DB 的检查，`run-lint.sh` 引入该脚本。

---

### DESIGN-03 🟡 中：`update-hot.py` 用路径 stem 替代真实 title

**文件**：`update-hot.py:13-15`

**问题描述**：`extract_title()` 将路径 stem 做大写转换（`agent-loop` → `Agent Loop`），丢失中文 title（如"Agent 循环机制"）。

**修复**：读取 frontmatter 获取真实 title，路径转换仅作降级兜底：

```python
import re, yaml

WIKI_ROOT = Path(__file__).parent.parent.parent

def extract_title(file_path: str) -> str:
    full_path = WIKI_ROOT / file_path
    if full_path.exists():
        try:
            text = full_path.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                if fm.get('title'):
                    return str(fm['title'])
        except Exception:
            pass
    return Path(file_path).stem.replace('-', ' ').title()  # 降级兜底
```

---

### DESIGN-04 🟡 中：hot.md 无条目上限，持续膨胀

**文件**：`update-hot.py`

**问题描述**：每次 ingest 追加条目，无老化机制，长期运行后 hot.md 超出合理体积，失去节省 token 的意义。

**修复**：每区域保留最新 20 条，超限 FIFO 淘汰：

```python
MAX_ENTRIES_PER_SECTION = 20

def trim_section(lines: list, section_prefix: str) -> list:
    result, entries, in_section = [], [], False
    for line in lines:
        if line.startswith(section_prefix):
            in_section, result = True, result + [line]
        elif in_section and (line.startswith('###') or line.startswith('##')):
            result.extend(entries[-MAX_ENTRIES_PER_SECTION:])
            result.append(line)
            in_section = False
        elif in_section and line.startswith('- '):
            entries.append(line)
        else:
            result.append(line)
    if in_section:
        result.extend(entries[-MAX_ENTRIES_PER_SECTION:])
    return result
```

---

### DESIGN-05 🟡 中：`check-config-sync.py` 缺少 8f 跨主题引用检查

**文件**：`check-config-sync.py`

**问题描述**：CLAUDE.md 步骤 8f 规定检查 L3 `[[wikilink]]` 是否引用了其他 domain 的概念，但脚本完全未实现（依赖 SQLITE-06 wikilinks 表后可实现）。

**实现框架**：

```python
# === 8f: 跨主题引用检查 ===
for n in notes:
    if n.get('layer') != 'L3':
        continue
    own_domain = (n.get('processing_path') or '/').split('/')[0]
    path = ROOT / n['_path']
    try:
        text = path.read_text(encoding='utf-8')
        links = re.findall(r'\[\[([^\]|#]+)', text)
        for slug in links:
            # 查 wikilinks 表获取 target 的 topic domain
            # 跨域引用报 WARN（不阻断，仅提示确认）
            pass
    except Exception:
        continue
```

---

### DESIGN-06 🟢 低：缺少 Stop Hook 自动捕获机制

**问题描述**：参考工程有 `.claude/hooks/wiki-stop-capture.sh`，会话结束时自动判断是否提示执行 quick ingest，实现被动知识沉淀。当前工程 `.claude/` 目录仅有 `scheduled_tasks.json`，无 Hook 配置。

**实现方向**：参照 obsidian-wiki `.claude/hooks/wiki-stop-capture.sh` 移植，判断条件：
- 文件修改调用（Write/Edit）> 0，或
- Shell 调用（Bash）≥ 4

满足条件时退出码 2 + stderr 消息，触发 Claude 提示用户执行 ingest。

---

## 第三部分：Skill / 工具链补全

### SKILL-01 新增 `check-db-health.py`（知识库健康仪表盘）

整合基于 DB 的 lint 检查，同时提供 status 统计输出：

```sql
-- 层级统计
SELECT layer, kind, status, COUNT(*) FROM notes GROUP BY layer, kind, status;

-- 近 7 天活动
SELECT COUNT(*) FROM notes WHERE updated >= date('now', '-7 days');

-- 死链（依赖 SQLITE-06）
SELECT COUNT(*) FROM wikilinks WHERE target_path IS NULL;

-- 孤立页面（零反链）
SELECT COUNT(*) FROM notes n
WHERE NOT EXISTS (SELECT 1 FROM wikilinks w WHERE w.target_slug = n.path);

-- Draft 超 30 天
SELECT COUNT(*) FROM notes
WHERE status='draft' AND julianday('now') - julianday(updated) > 30;

-- Summary 不足 200 字
SELECT path, length(summary) FROM notes
WHERE summary IS NOT NULL AND length(summary) < 200;
```

### SKILL-02 新增 `--full-rebuild` 参数

`index-notes.py` 支持 `--full-rebuild`，触发跳过触发器的全量重建（方案 B），用于索引损坏时一键恢复：

```bash
python 0100-wiki-meta/scripts/index-notes.py --full-rebuild
```

### SKILL-03 `skill-lint.md` 与 `run-lint.sh` 对齐

对照 `skill-lint.md` 内容，补全 `run-lint.sh` 至覆盖所有文档化检查项（见 DESIGN-02）。目标：`run-lint.sh` 全程无 `(manual check)` 行。

### SKILL-04 缺少 `wiki-synthesize`（跨文件综合分析）

当前 ingest 只支持单源→L3 纵向提炼，无法对多个 L2 横向综合。

新增 `skill-synthesize.md`，流程：
1. 用户指定多个 L2 文件或 topic 目录
2. 读取各 L2 的"核心提炼"区
3. 横向对比，提炼共性和差异
4. 生成 L3 concept，`source` 列表指向所有参与 L2

### SKILL-05 缺少 Stop Hook（见 DESIGN-06）

参照 obsidian-wiki 实现，添加 `.claude/hooks/wiki-stop-capture.sh` 和对应 `settings.local.json` 配置。

---

## 第四部分：架构设计层问题

### ARCH-01 🟡 中：topic 编号手动维护，存在注册表负债

**问题描述**：当前工程用 `{编号}-{主题名}` 硬编码目录（`3000-Agent`、`3001-RAG`），新增主题需人工分配编号，`topics.yaml` 的 `active` 列表与实际目录是两套真相，需要 `check-config-sync.py` 持续维持同步，属于设计负债。

参考工程用无编号 category（concepts/entities/skills 等），靠 `processing_path` 定位，扩展无需编号协调。

**改进方案**：在 `topics.yaml` 中增加 `next_id` 自增字段，由脚本统一分配编号，禁止人工填写：

```yaml
# topics.yaml 新增字段
meta:
  next_id: 3010   # 下次新建 topic 自动取此值并 +1

domains:
  AI技术:
    range: [3000, 3099]
    next_id: 3002  # 域内自增
    active:
      - 3000-Agent
      - 3001-RAG与检索
```

`skill-ingest.md` 步骤 1 调用脚本自动分配，而非让 Claude 主观选号。

---

### ARCH-02 🟡 中：L2→L3 双向索引断裂

**问题描述**：参考工程 `.manifest.json` 明确记录每个源文件派生了哪些页面（`pages_created`/`pages_updated`），关系可程序化查询。当前工程虽设计了 `ingested_files + file_produces` 表，但：

1. 这两张表因 SQLITE-01 问题从未被创建
2. 即便修复后，`index-notes.py` 也不填充 `file_produces`——L3 的 `source` 字段只是文本，没有反向写入关联表

**结果**：无法回答"这个 L2 派生了哪些 L3？"、"删除一个 L2 会影响哪些 L3？"

**修复方案**：`index-notes.py` 索引 L3 时，读取 `source` 字段反向填充 `file_produces`：

```python
# index-notes.py — 索引 L3 时补充填充 file_produces
if layer == 'L3':
    sources = meta.get('source') or []
    if isinstance(sources, str):
        sources = [sources]
    for src_path in sources:
        # 查找对应 L2 的 ingested_files 记录
        cur.execute(
            "SELECT id FROM ingested_files WHERE source_path LIKE ?",
            (f"%{src_path}",)
        )
        row = cur.fetchone()
        if row:
            cur.execute("""
                INSERT OR IGNORE INTO file_produces
                (source_file_id, produced_page_path, page_layer)
                VALUES (?, ?, 'L3')
            """, (row[0], rel_path))
```

---

### DESIGN-07 🟡 中：`skill-query.md` 未调用 SQLite，`query.py` 闲置

**文件**：`0100-wiki-meta/scripts/skill-query.md`、`query.py`

**问题描述**：`skill-query.md` 定义的检索流程为 `hot.md → rg 文件系统 → 读全文`，完全未引导 Claude 调用已有的 `query.py`（FTS5 全文检索）。执行 query skill 时，Claude 用 `rg` 扫描文件系统，而 `query.py` 闲置。

**影响**：
- `rg` 扫描无排序，FTS5 BM25 有相关性排序
- `rg` 不分层（L3 优先→L2→L1），`query.py` 已实现分层逻辑
- 大型 vault 下 `rg` 比 FTS5 慢 3-5 倍

**修复**：`skill-query.md` 步骤 2 改为优先调用 `query.py`，FTS5 无结果时降级到 `rg`：

```markdown
### 步骤 2：SQLite FTS5 检索（优先）

```bash
python "D:\obsidian\0100-wiki-meta\scripts\query.py" "<关键词>" 8
```

返回结果直接含 layer/title/summary，跳过文件系统扫描。
若结果为空或不足，降级到步骤 2b（rg 兜底）。

### 步骤 2b：rg 兜底（FTS5 无匹配时）

```bash
rg "关键词" 0101-wiki-topics/ 0102-wiki-concepts/
```
```

---

## 实施优先级

| 优先级 | 任务 ID | 描述 | 工作量 |
|---|---|---|---|
| P0 | SQLITE-01 | 修复 `ingested_files` 表缺失 | S |
| P0 | SQLITE-04 | 修复 `updated_ts` 语义错误 | S |
| P0 | DESIGN-01 | 统一图片路径命名规范 | S |
| P1 | SQLITE-02 | 增量索引实现 | M |
| P1 | SQLITE-03 | PRAGMA 统一配置 | S |
| P1 | SQLITE-06 | wikilinks 表 + 死链查询 | M |
| P1 | DESIGN-03 | hot.md title 提取修复 | S |
| P1 | DESIGN-04 | hot.md 条目上限 | S |
| P2 | DESIGN-02 | run-lint.sh 补全 + check-db-health.py | L |
| P2 | SQLITE-05 | 相似度检测增强 | M |
| P2 | SQLITE-07/08 | check-config-sync + query 增强 | M |
| P2 | ARCH-02 | L2→L3 双向索引（file_produces 填充）| M |
| P2 | DESIGN-07 | skill-query.md 改为优先调用 query.py | S |
| P3 | ARCH-01 | topics.yaml next_id 自增，禁止人工选号 | M |
| P3 | SKILL-01~05 | 工具链补全 | XL |

**工作量说明**：S ≈ 1-2h，M ≈ 半天，L ≈ 1 天，XL ≈ 多天

---

## 验收标准

| # | 标准 |
|---|---|
| 1 | `python init-db.py` 后 `.tables` 包含 `ingested_files`、`file_produces`、`wikilinks` |
| 2 | `python delta-track.py check <文件>` 不抛 `OperationalError` |
| 3 | 第二次运行 `index-notes.py`（无变更时）耗时 < 1s，输出 `新增 0，更新 0，删除 0` |
| 4 | `run-lint.sh` 全程无 `(manual check)` 行，所有检查均有脚本输出 |
| 5 | hot.md 每区域条目数 ≤ 20，新建后 title 字段显示中文 |
| 6 | `check-config-sync.py` 退出码 0 时完整覆盖 8a-8g 所有检查项 |
| 7 | `query.py --dead-links` 可输出死链列表 |
| 8 | `query.py --stats` 可输出层级分布统计 |
