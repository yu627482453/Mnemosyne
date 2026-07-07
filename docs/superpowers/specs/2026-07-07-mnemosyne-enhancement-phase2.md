# Mnemosyne 系统优化增强 Phase 2

**文档版本**: 1.0  
**创建日期**: 2026-07-07  
**基于**: Phase 1 (2026-07-06) 完成后的系统状态

---

## 执行摘要

Phase 1 已完成关键的SQLite基础设施优化（P0+P1+P2，共13项任务）。Phase 2 聚焦于：
1. **补全Lint体系**：实现剩余7项健康检查
2. **运维优化**：修复34个死链，治理2个孤立页面
3. **可选增强**：图谱分析、批量工具、文档完善

**关键决策**：
- ❌ **不实现index.md**（冗余、一致性风险、不可扩展）
- ✅ **SQLite为唯一索引**（已完善，无需额外视图）
- ✅ **优先Lint完善**（质量保障优先于功能扩展）

---

## 当前系统状态

### ✅ 已完成（Phase 1）

**P0 - 关键Bug修复（6项）**
- [x] SQLite表缺失（ingested_files, file_produces, wikilinks）
- [x] Schema版本控制（user_version）
- [x] PRAGMA优化（WAL, NORMAL, cache_size）
- [x] 增量索引（delta-track.py集成）
- [x] updated_ts修正（使用note实际更新时间）
- [x] Wikilinks提取与L2→L3反向索引

**P1 - 设计标准化（2项）**
- [x] 图片命名（timestamp: `{slug}-{YYYYMMDDHHmmss}.{ext}`）
- [x] hot.md FIFO限制（MAX_ENTRIES_PER_SECTION = 20）
- [x] Query优先级（query.py FTS5 优先于 rg）

**P2 - 功能增强（5项）**
- [x] 相似度检测（双通道：string + FTS5 BM25）
- [x] 配置同步反向检查（stale index清理）
- [x] Query过滤器（layer/kind/topic/backlinks/dead_links）
- [x] DB健康检查聚合（check-db-health.py）
- [x] Lint编排脚本（run-lint.sh框架）

### 📊 系统指标

```
总页面: 22 (L2: 2, L3: 20)
总链接: 139
死链: 34 (23图片 + 11概念)
孤立页面: 2
Lint检查: 3/10 已实现
```

---

## Phase 2 优化任务概览

### P0 - Lint体系补全（7项，CRITICAL）

| 编号 | 检查项 | 当前状态 | 优先级 |
|------|--------|----------|--------|
| L4 | L2结构完整性 | 待实现 | P0 |
| L5 | 文件名格式 | 待实现 | P0 |
| L6 | resource_refs一致性 | 待实现 | P0 |
| L7 | 远程图片残留 | 待实现 | P0 |
| L8 | Tags格式 | 待实现 | P0 |
| L9 | Summary范围 | 待实现 | P0 |
| L10 | Topic注册 | 部分实现 | P0 |

### P1 - 运维治理 + 核心增强（4项，HIGH）⭐️

| 编号 | 任务 | 来源 | 当前状态 | 优先级 |
|------|------|------|----------|--------|
| M1 | 修复34个死链 | Phase 1分析 | 待处理 | P1 |
| M2 | 治理2个孤立页面 | Phase 1分析 | 待处理 | P1 |
| **E4** | **置信度跟踪系统** | **obsidian-wiki** | **待实施** | **P1** |
| **E5** | **关系类型化** | **obsidian-wiki** | **待实施** | **P1** |

### P2 - 可选增强（4项，OPTIONAL）

| 编号 | 功能 | 来源 | 价值 | 优先级 |
|------|------|------|------|--------|
| E1 | 图谱分析工具 | Phase 1规划 | 发现知识孤岛 | P2 |
| E2 | 批量操作CLI | Phase 1规划 | 提升运维效率 | P2 |
| E3 | 使用文档 | Phase 1规划 | 降低上手门槛 | P2 |
| **E6** | **批量并行优化** | **obsidian-wiki** | **效率提升2-3倍** | **P2** |

---

## 借鉴obsidian-wiki特性

### 核心对比分析

通过对比`D:\gitRepository\obsidian-wiki`的skill设计，发现以下高价值特性：

| 特性 | Mnemosyne当前 | obsidian-wiki | 借鉴价值 |
|------|--------------|---------------|---------|
| **置信度跟踪** | ❌ | base_confidence + provenance markers | 🟢高 |
| **关系类型化** | ❌ | relationships字段（8种类型） | 🟢高 |
| **批量并行** | 主题分批建议 | 自动batch-plan并行 | 🟢高 |
| **代码提取** | ❌ | AST零token提取 | 🟡中 |
| **学术论文** | ❌ | 图表+方程+表格提取 | 🟡中 |

### 决策：整合到Phase 2

基于价值分析，将**置信度系统**和**关系类型化**从可选增强提升到P1，与运维治理并列。

---

## P0 - Lint体系补全

### L4: L2结构完整性检查

**问题**：L2文件应包含两个必需区域，但目前无自动化校验。

**必需区域**：
1. **核心提炼区**（`---` 分隔线之上）
   - 核心提炼（概括论证逻辑和上下文关系）
   - 关键概念（wikilink列表）
   - 原文要点（章节大纲+关键论点）
   - 来源（作者、机构、原文链接）

2. **原文笔记区**（`---` 分隔线之下）
   - 原文中文翻译
   - 保留段落层次
   - 代码块保留核心逻辑

**实现方案**：

创建 `0100-wiki-meta/scripts/check-l2-structure.py`：

```python
#!/usr/bin/env python3
"""检查 L2 文件结构完整性"""
import sys, re
from pathlib import Path

def check_l2_structure(md_file: Path) -> list[str]:
    """返回问题列表，空列表表示通过"""
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    # 移除frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # 检查是否有分隔线
    if '\n---\n' not in content:
        issues.append("缺少核心提炼区与原文笔记区的分隔线（---）")
        return issues
    
    upper, lower = content.split('\n---\n', 1)
    
    # 检查核心提炼区关键元素
    required_sections = ['核心提炼', '关键概念', '原文要点', '来源']
    for section in required_sections:
        if section not in upper:
            issues.append(f"核心提炼区缺少「{section}」段落")
    
    # 检查原文笔记区是否为空
    if len(lower.strip()) < 100:
        issues.append("原文笔记区内容过少（<100字符）")
    
    return issues

# 主逻辑：扫描所有L2文件
```

**集成**：在 `run-lint.sh` 第74行替换占位符：
```bash
run_check "L2 结构完整性" "0100-wiki-meta/scripts/check-l2-structure.py" "WARNING"
```

**验收标准**：
- [ ] 检测到缺少分隔线的L2文件
- [ ] 检测到缺少必需段落的L2文件
- [ ] 通过测试：创建不完整L2，运行检查，验证捕获

---

### L5: 文件名格式检查

**问题**：CLAUDE.md规定文件名命名规则，但目前无自动化校验。

**命名规则**：
- 空格 → `-`
- `.` → `_`（仅最后一个`.`是扩展名）
- 特殊字符（`/ : * ? " < > | + #`）→ `_`
- 统一英文kebab-case全小写

**实现方案**：

创建 `0100-wiki-meta/scripts/check-filename-format.py`：

```python
#!/usr/bin/env python3
"""检查文件名格式规范"""
import sys, re
from pathlib import Path

INVALID_CHARS = r'[/:*?"<>|+#\s]'  # 空格+特殊字符
MULTIPLE_DOTS = r'\..*\.'  # 多个点（扩展名前）

def check_filename(path: Path) -> list[str]:
    """返回文件名问题列表"""
    issues = []
    name = path.stem  # 不含扩展名
    
    # 检查非法字符
    if re.search(INVALID_CHARS, name):
        issues.append(f"文件名包含非法字符或空格: {name}")
    
    # 检查多个点
    if re.search(MULTIPLE_DOTS, name):
        issues.append(f"文件名扩展名前有多余的点: {name}")
    
    # 检查大小写（应全小写）
    if name != name.lower():
        issues.append(f"文件名应全小写: {name}")
    
    # 检查连续符号
    if '--' in name or '__' in name:
        issues.append(f"文件名有连续符号: {name}")
    
    return issues

# 主逻辑：扫描所有L2/L3文件
```

**集成**：在 `run-lint.sh` 第80行替换占位符。

**验收标准**：
- [ ] 检测到含空格的文件名
- [ ] 检测到含大写字母的文件名
- [ ] 检测到多余点号的文件名

---

### L6: resource_refs一致性检查

**问题**：frontmatter的`resource_refs`字段应与实际图片路径1:1匹配。

**检查逻辑**：
1. 读取frontmatter的`resource_refs`列表
2. 扫描正文中的`![[image]]`引用
3. 验证双向匹配：
   - frontmatter中的每个路径在正文中被引用
   - 正文中的每个图片在frontmatter中登记

**实现方案**：

创建 `0100-wiki-meta/scripts/check-resource-refs.py`：

```python
#!/usr/bin/env python3
"""检查 resource_refs 字段与实际图片引用的一致性"""
import sys, re, yaml
from pathlib import Path

def extract_image_refs(content: str) -> set[str]:
    """提取正文中的图片引用 ![[filename]]"""
    pattern = r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|svg|webp))\]\]'
    return set(re.findall(pattern, content, re.IGNORECASE))

def check_resource_refs_consistency(md_file: Path) -> list[str]:
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []
    
    fm = yaml.safe_load(m.group(1)) or {}
    refs_in_fm = set(fm.get('resource_refs') or [])
    refs_in_content = extract_image_refs(content)
    
    # 双向检查
    orphaned_fm = refs_in_fm - refs_in_content
    orphaned_content = refs_in_content - refs_in_fm
    
    if orphaned_fm:
        issues.append(f"resource_refs中有未使用的图片: {orphaned_fm}")
    
    if orphaned_content:
        issues.append(f"正文图片未登记到resource_refs: {orphaned_content}")
    
    return issues

# 主逻辑
```

**集成**：在 `run-lint.sh` 第86行替换占位符。

**验收标准**：
- [ ] 检测到frontmatter中有但正文未用的图片
- [ ] 检测到正文中有但frontmatter未登记的图片
- [ ] 通过测试：故意制造不一致，验证捕获

---

### L7: 远程图片残留检查

**问题**：ingest过程应将所有远程图片下载到本地，正文中不应残留http/https图片链接。

**检查逻辑**：
- 扫描正文中的`![alt](http://...)` 或 `![alt](https://...)`
- 报告所有远程图片URL

**实现方案**：

创建 `0100-wiki-meta/scripts/check-remote-images.py`：

```python
#!/usr/bin/env python3
"""检查正文中是否残留远程图片链接"""
import sys, re
from pathlib import Path

REMOTE_IMAGE_PATTERN = r'!\[.*?\]\((https?://[^\)]+)\)'

def check_remote_images(md_file: Path) -> list[str]:
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    matches = re.findall(REMOTE_IMAGE_PATTERN, content)
    if matches:
        for url in matches:
            issues.append(f"残留远程图片: {url}")
    
    return issues

# 主逻辑：扫描所有L2/L3文件
```

**集成**：在 `run-lint.sh` 第92行替换占位符。

**验收标准**：
- [ ] 检测到含http://图片的文件
- [ ] 检测到含https://图片的文件
- [ ] 通过测试：故意添加远程图片，验证捕获

---

### L8: Tags格式检查

**问题**：CLAUDE.md规定tags应5-10个，无空格，连字符连接，但目前无自动化校验。

**Tags规则**：
- 数量：5-10个
- 格式：kebab-case（小写，连字符连接）
- 禁止：空格、大写字母、下划线

**实现方案**：

创建 `0100-wiki-meta/scripts/check-tags-format.py`：

```python
#!/usr/bin/env python3
"""检查 tags 字段格式规范"""
import sys, re, yaml
from pathlib import Path

TAG_PATTERN = r'^[a-z0-9]+(-[a-z0-9]+)*$'  # kebab-case

def check_tags_format(md_file: Path) -> list[str]:
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []
    
    fm = yaml.safe_load(m.group(1)) or {}
    tags = fm.get('tags') or []
    
    # 检查数量
    if len(tags) < 5:
        issues.append(f"tags数量不足（{len(tags)}/5）")
    elif len(tags) > 10:
        issues.append(f"tags数量过多（{len(tags)}/10）")
    
    # 检查格式
    for tag in tags:
        if not isinstance(tag, str):
            continue
        
        if ' ' in tag:
            issues.append(f"tag含空格: '{tag}'")
        elif not re.match(TAG_PATTERN, tag):
            issues.append(f"tag格式不符（应kebab-case）: '{tag}'")
    
    return issues

# 主逻辑
```

**集成**：在 `run-lint.sh` 第98行替换占位符。

**验收标准**：
- [ ] 检测到tags数量<5的文件
- [ ] 检测到tags数量>10的文件
- [ ] 检测到含空格/大写的tag
- [ ] 通过测试：故意制造不规范tags，验证捕获

---

### L9: Summary范围检查

**问题**：CLAUDE.md规定summary字段应≥200字，但目前无自动化校验。

**检查逻辑**：
- 提取frontmatter的summary字段
- 计算字符数（中文按1个字符计）
- 报告<200字的文件

**实现方案**：

创建 `0100-wiki-meta/scripts/check-summary-length.py`：

```python
#!/usr/bin/env python3
"""检查 summary 字段长度"""
import sys, re, yaml
from pathlib import Path

MIN_SUMMARY_LENGTH = 200

def check_summary_length(md_file: Path) -> list[str]:
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []
    
    fm = yaml.safe_load(m.group(1)) or {}
    summary = fm.get('summary', '')
    
    if not summary:
        issues.append("缺少summary字段")
    elif len(summary) < MIN_SUMMARY_LENGTH:
        issues.append(f"summary过短（{len(summary)}/{MIN_SUMMARY_LENGTH}字符）")
    
    return issues

# 主逻辑：扫描所有L2/L3文件
```

**集成**：在 `run-lint.sh` 第104行替换占位符。

**验收标准**：
- [ ] 检测到summary<200字的文件
- [ ] 检测到缺少summary的文件
- [ ] 通过测试：故意制造短summary，验证捕获

---

### L10: Topic注册检查

**问题**：check-config-sync.py已部分实现（检查L2 topic是否在topics.yaml active列表），但需要独立的检查脚本供run-lint.sh调用。

**检查逻辑**：
1. 加载topics.yaml的active列表
2. 扫描所有L2文件的topic字段
3. 验证每个topic都在active列表中

**实现方案**：

创建 `0100-wiki-meta/scripts/check-topic-registration.py`：

```python
#!/usr/bin/env python3
"""检查 L2 topic 是否已注册到 topics.yaml"""
import sys, re, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOPICS_FILE = ROOT / "0100-wiki-meta" / "configs" / "topics.yaml"

def load_active_topics() -> set[str]:
    """加载topics.yaml中的active主题"""
    cfg = yaml.safe_load(TOPICS_FILE.read_text(encoding='utf-8'))
    active = set()
    for domain_data in (cfg.get('domains') or {}).values():
        active.update(domain_data.get('active') or [])
    return active

def check_topic_registration() -> list[str]:
    issues = []
    active_topics = load_active_topics()
    
    # 扫描所有L2文件
    for md in ROOT.rglob("*.md"):
        rel = str(md.relative_to(ROOT)).replace('\\', '/')
        if '.trash' in rel or '.git' in rel:
            continue
        
        content = md.read_text(encoding='utf-8')
        m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not m:
            continue
        
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get('layer') != 'L2':
            continue
        
        topic = fm.get('topic')
        if topic and topic not in active_topics:
            issues.append(f"{rel}: topic '{topic}' 未注册到 topics.yaml")
    
    return issues

# 主逻辑
```

**集成**：在 `run-lint.sh` 第111行更新占位符：
```bash
run_check "Topic 注册" "0100-wiki-meta/scripts/check-topic-registration.py" "WARNING"
```

**验收标准**：
- [ ] 检测到未注册的topic
- [ ] 通过测试：故意使用未注册topic，验证捕获
- [ ] 与check-config-sync.py结果一致

---

## P1 - 运维治理

### M1: 修复34个死链

**当前状态**：
```
死链总数: 34
- 图片死链: 23个
- 概念死链: 11个
```

**问题分析**：
1. **图片死链**：图片文件路径变更或文件缺失
2. **概念死链**：引用的概念页面未创建，或slug不匹配

**实现方案**：

**步骤1：生成死链报告**
```bash
python 0100-wiki-meta/scripts/query.py --dead-links > dead-links-report.txt
```

**步骤2：批量修复图片死链**

创建 `0100-wiki-meta/scripts/fix-dead-image-links.py`：
```python
#!/usr/bin/env python3
"""修复图片死链"""
import sys, re, sqlite3
from pathlib import Path

def fix_image_links():
    """扫描死链，尝试自动修复"""
    conn = sqlite3.connect('.wiki.db')
    cur = conn.cursor()
    
    # 查询图片死链
    cur.execute("""
        SELECT DISTINCT source_path, target_slug
        FROM wikilinks
        WHERE target_path IS NULL
        AND target_slug LIKE '%.png' OR target_slug LIKE '%.jpg'
    """)
    
    for source_path, broken_slug in cur.fetchall():
        # 在0001-resource/中搜索匹配的图片
        candidates = list(Path('0001-resource').rglob(f"*{broken_slug}*"))
        
        if len(candidates) == 1:
            # 唯一匹配，自动替换
            fix_link_in_file(source_path, broken_slug, candidates[0])
        elif len(candidates) > 1:
            # 多个匹配，需要人工决策
            print(f"多个候选：{source_path} → {broken_slug}")
            for c in candidates:
                print(f"  - {c}")
        else:
            # 无匹配，标记为待处理
            print(f"无匹配：{source_path} → {broken_slug}")

def fix_link_in_file(file_path, old_slug, new_path):
    """替换文件中的死链"""
    # 实现细节：读取文件，替换链接，写回
    pass

# 主逻辑
```

**步骤3：批量修复概念死链**

分两种情况处理：
1. **概念已存在但slug不匹配**：更新wikilink
2. **概念确实未创建**：添加到planned_links或创建stub页面

**验收标准**：
- [ ] 图片死链从23降至<5
- [ ] 概念死链从11降至<3
- [ ] 所有修复记录在0109-log/

---

### M2: 治理2个孤立页面

**当前状态**：
```
孤立页面: 2个（无入链的L2/L3页面）
```

**问题分析**：
孤立页面无法通过正常的wikilink导航到达，降低知识可发现性。

**治理策略**：

**选项A：创建入链**
- 在相关topic页面（0101-wiki-topics/）添加引用
- 在相关concept页面添加"参见"链接

**选项B：归档**
- 评估页面价值
- 若过时或冗余，移入.trash/

**实现步骤**：

1. **识别孤立页面**：
```bash
python 0100-wiki-meta/scripts/check-db-health.py | grep orphaned
```

2. **逐个评估**：
   - 阅读页面内容
   - 判断价值（高/中/低）
   - 决策：创建入链 or 归档

3. **执行治理**：
   - 创建入链：在合适位置添加`[[page]]`引用
   - 归档：`git mv {page} .trash/`

**验收标准**：
- [ ] 孤立页面降至0
- [ ] 所有决策记录在0109-log/
- [ ] 重新运行check-db-health.py，orphaned=0

---

## SQLite Version 2 迁移（E4+E5统一）

**说明**：E4置信度系统和E5关系类型化都需要扩展SQLite schema，统一在version 2迁移中完成。

### 完整迁移脚本

修改 `0100-wiki-meta/scripts/init-db.py`，在version 1检查后添加：

```python
if version < 2:
    print("开始 Schema Version 2 迁移...")
    
    # ========== E4: 置信度系统 ==========
    
    # 添加confidence虚拟列（从layer_data JSON提取）
    try:
        cur.execute("""
            ALTER TABLE notes ADD COLUMN confidence REAL
            GENERATED ALWAYS AS (CAST(json_extract(layer_data, '$.confidence') AS REAL)) VIRTUAL
        """)
        print("  [✓] 添加confidence虚拟列")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e).lower():
            raise
        print("  [!] confidence列已存在，跳过")
    
    # 创建confidence索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON notes(confidence)")
    print("  [✓] 创建confidence索引")
    
    # ========== E5: 关系类型化 ==========
    
    # 创建relationships表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT NOT NULL,
            target_path TEXT NOT NULL,
            rel_type TEXT NOT NULL CHECK(rel_type IN (
                'extends', 'implements', 'contradicts',
                'derived_from', 'uses', 'replaces', 'related_to'
            )),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_path, target_path, rel_type)
        )
    """)
    print("  [✓] 创建relationships表")
    
    # 创建relationships索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type)")
    print("  [✓] 创建relationships索引")
    
    # 升级版本号
    cur.execute("PRAGMA user_version = 2")
    print("  [✓] Schema升级到version 2完成")
```

### 验证迁移成功

运行后验证：

```bash
# 检查版本号
sqlite3 .wiki.db "PRAGMA user_version"  # 应输出：2

# 检查confidence虚拟列
sqlite3 .wiki.db "PRAGMA table_info(notes)" | grep confidence

# 检查relationships表
sqlite3 .wiki.db ".schema relationships"

# 检查索引
sqlite3 .wiki.db ".indexes relationships"
```

---

### E4: 置信度跟踪系统（新增，来自obsidian-wiki）

**价值**：将知识可信度量化，区分"事实"与"推理"，支持高级图谱分析。

**obsidian-wiki实现要点**：
- Frontmatter字段：`base_confidence`（0.0-1.0）、`provenance`（extracted/inferred/ambiguous比例）
- 正文标记：`^[inferred]`（推理内容）、`^[ambiguous]`（有争议内容）
- 计算公式：`base_confidence = min(N_sources/3, 1.0) × 0.5 + avg_quality × 0.5`

**Mnemosyne适配方案**：

**步骤1：Schema扩展**

修改 `0100-wiki-meta/configs/schema.yaml`：

```yaml
# L2添加（L2是原文，高置信度）
confidence: { type: number, min: 0.8, max: 1.0, description: "知识置信度" }
provenance: { type: object, description: "来源比例：extracted/inferred/ambiguous，三者和≈1.0" }

# L3添加（L3是派生，中高置信度）
confidence: { type: number, min: 0.6, max: 1.0, description: "知识置信度" }
provenance: { type: object, description: "来源比例：extracted/inferred/ambiguous，三者和≈1.0" }
```

**注意**：保持与当前schema.yaml的DSL格式一致（使用`min/max`，而非`minimum/maximum`）。

**步骤2：SQLite表扩展（补充索引支持）**

修改 `0100-wiki-meta/scripts/init-db.py`，在version 2迁移中添加：

```python
if version < 2:
    # 添加confidence虚拟列（从layer_data JSON提取）
    try:
        cur.execute("""
            ALTER TABLE notes ADD COLUMN confidence REAL
            GENERATED ALWAYS AS (CAST(json_extract(layer_data, '$.confidence') AS REAL)) VIRTUAL
        """)
        print("  [✓] 添加confidence虚拟列")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e).lower():
            raise
    
    # 创建confidence索引（支持按置信度过滤查询）
    cur.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON notes(confidence)")
    print("  [✓] 创建confidence索引")
    
    # 创建relationships表（见E5步骤2）
    
    cur.execute("PRAGMA user_version = 2")
    print("  [✓] 升级到version 2")
```

**用途**：支持以下查询场景：
```sql
-- 查询高置信度页面
SELECT path, title, confidence FROM notes WHERE confidence >= 0.8 ORDER BY confidence DESC;

-- 查询低置信度需补充来源的页面
SELECT path, title, confidence FROM notes WHERE confidence < 0.7 AND layer = 'L3';
```

**步骤3：index-notes.py集成**

在步骤5（创建L2/L3）增加子步骤：

```markdown
### 5c. 计算置信度和来源标注

**L2置信度**：
- 直接引用原文：confidence = 0.95
- provenance: {extracted: 0.9, inferred: 0.1, ambiguous: 0}

**L3置信度**：
- 单一L2来源：confidence = 0.7
- 多个L2来源：confidence = min(N/3, 1.0) × 0.5 + 0.7 × 0.5
- 标注推理性内容：`概念X通过Y实现^[inferred]`
- 统计标记比例：provenance: {extracted: 0.4, inferred: 0.5, ambiguous: 0.1}
```

**index-notes.py代码修改**：

同时修改 `0100-wiki-meta/scripts/index-notes.py`，提取confidence和provenance到layer_data：

```python
def index_notes():
    # ... 现有代码 ...
    
    for md_file in WIKI_ROOT.rglob("*.md"):
        # ... 解析frontmatter ...
        meta = yaml.safe_load(m.group(1)) or {}
        
        # 构建layer_data（JSON字段）
        layer_data = {}
        
        if layer == 'L2':
            layer_data['topic'] = meta.get('topic', '')
        elif layer == 'L3':
            layer_data['processing_path'] = meta.get('processing_path', '')
        
        # ===== E4: 提取置信度和来源 =====
        confidence = meta.get('confidence')
        provenance = meta.get('provenance')
        
        if confidence is not None:
            layer_data['confidence'] = confidence
        
        if provenance is not None:
            layer_data['provenance'] = provenance
        # ===================================
        
        layer_data_json = json.dumps(layer_data, ensure_ascii=False)
        
        # 插入notes表（layer_data包含confidence）
        cur.execute("""INSERT OR REPLACE INTO notes (..., layer_data) VALUES (..., ?)""",
                   (..., layer_data_json))
```

**关键点**：
- confidence/provenance从frontmatter提取后存入layer_data JSON
- SQLite虚拟列自动从JSON提取confidence用于索引查询
- provenance保留在JSON中供Lint工具读取

**步骤4：Lint检查**

创建 `0100-wiki-meta/scripts/check-provenance.py`：

```python
#!/usr/bin/env python3
"""检查置信度和来源标注完整性"""
import sys, re, yaml
from pathlib import Path

def check_provenance(md_file: Path) -> list[str]:
    issues = []
    content = md_file.read_text(encoding='utf-8')
    
    # 提取frontmatter
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return []
    
    fm = yaml.safe_load(m.group(1)) or {}
    
    # 检查confidence字段
    conf = fm.get('confidence')
    if conf is None:
        issues.append("缺少confidence字段")
    elif not (0.0 <= conf <= 1.0):
        issues.append(f"confidence超出范围: {conf}")
    
    # 检查provenance字段
    prov = fm.get('provenance')
    if prov is None:
        issues.append("缺少provenance字段")
    else:
        total = prov.get('extracted', 0) + prov.get('inferred', 0) + prov.get('ambiguous', 0)
        # 容差±0.15（考虑四舍五入和估算误差）
        if abs(total - 1.0) > 0.15:
            issues.append(f"provenance比例和不为1.0（当前{total:.2f}，容差±0.15）")
        
        # 各比例范围检查
        for key in ['extracted', 'inferred', 'ambiguous']:
            val = prov.get(key, 0)
            if not (0 <= val <= 1):
                issues.append(f"provenance.{key}超出[0,1]范围: {val}")
    
    # 检查正文标记数量是否与provenance匹配
    body = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    inferred_count = len(re.findall(r'\^\[inferred\]', body))
    ambiguous_count = len(re.findall(r'\^\[ambiguous\]', body))
    
    # 估算正文总句子数（简单方法：按句号、问号、感叹号分割）
    sentences = len(re.findall(r'[。！？.!?]+', body))
    if sentences == 0:
        sentences = 1  # 避免除零
    
    inferred_ratio = inferred_count / sentences
    ambiguous_ratio = ambiguous_count / sentences
    
    # 阈值检查：如果provenance显示inferred>30%但标记占比<10%，可能遗漏标记
    if prov and prov.get('inferred', 0) > 0.3 and inferred_ratio < 0.1:
        issues.append(
            f"provenance显示inferred={prov.get('inferred'):.0%}，"
            f"但正文仅{inferred_count}处^[inferred]标记（占比{inferred_ratio:.0%}）"
        )
    
    # 反向检查：如果标记很多但provenance比例很低，可能估算不准
    if inferred_ratio > 0.3 and prov and prov.get('inferred', 0) < 0.2:
        issues.append(
            f"正文有{inferred_count}处^[inferred]标记（占比{inferred_ratio:.0%}），"
            f"但provenance显示inferred仅{prov.get('inferred'):.0%}"
        )
    
    return issues

# 主逻辑：扫描所有L2/L3文件
```

**步骤4：集成到run-lint.sh**

在run-lint.sh末尾增加检查项（新增L11）：

```bash
run_check "置信度和来源标注" "0100-wiki-meta/scripts/check-provenance.py" "WARNING"
```

**验收标准**：
- [ ] schema.yaml包含confidence和provenance字段
- [ ] skill-ingest.md包含置信度计算步骤
- [ ] check-provenance.py可检测缺失或不合理的置信度
- [ ] 通过测试：创建带/不带置信度的测试页面，验证捕获

---

### E5: 关系类型化（新增，来自obsidian-wiki）

**价值**：将隐式的语义关系显式化，支持精确的知识图谱分析和"技术演进"、"对比分析"等高级查询。

**obsidian-wiki实现要点**：
- Frontmatter `relationships` 字段，包含 target 和 type
- 允许的类型：extends/implements/contradicts/derived_from/uses/replaces/related_to
- SQLite索引支持关系查询

**Mnemosyne适配方案**：

**步骤1：Schema扩展**

修改 `0100-wiki-meta/configs/schema.yaml` L3部分：

```yaml
relationships: { type: list, description: "类型化关系列表：[{target: '[[slug]]', type: 'extends'}]" }
# 允许的type值：extends, implements, contradicts, derived_from, uses, replaces, related_to
```

**注意**：保持与当前schema.yaml的DSL格式一致（使用`type: list`，而非`type: array`）。

**步骤2：SQLite表扩展**

修改 `0100-wiki-meta/scripts/init-db.py`：

```python
# 在wikilinks表之后增加
cur.execute("""CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    rel_type TEXT NOT NULL CHECK(rel_type IN (
        'extends', 'implements', 'contradicts', 
        'derived_from', 'uses', 'replaces', 'related_to'
    )),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_path, target_path, rel_type)
)""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_path)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_path)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type)")
```

**步骤3：index-notes.py扩展**

在index_notes()函数中增加relationships提取：

```python
# 提取relationships
rels = meta.get('relationships') or []
for rel in rels:
    target_slug = rel.get('target', '').strip('[]')
    rel_type = rel.get('type', 'related_to')
    
    # 解析target_path
    target_path = None
    for candidate in WIKI_ROOT.rglob(f"{target_slug}.md"):
        rel_c = str(candidate.relative_to(WIKI_ROOT)).replace('\\', '/')
        if '.trash' not in rel_c and '.git' not in rel_c:
            target_path = rel_c
            break
    
    cur.execute("""INSERT OR IGNORE INTO relationships
        (source_path, target_path, rel_type)
        VALUES (?, ?, ?)""", (rel_path, target_path, rel_type))
```

**步骤4：skill-ingest.md扩展**

在步骤5（创建L3）增加关系识别：

```markdown
### 5d. 识别类型化关系

扫描L2原文和L3内容，识别明确的关系模式：

| 关键词模式 | 关系类型 | 示例 |
|-----------|---------|------|
| "X基于Y"、"X派生自Y" | derived_from | Transformer派生自Attention |
| "X替代了Y"、"X取代Y" | replaces | BERT替代了LSTM |
| "X使用Y"、"X调用Y" | uses | Agent使用Tool |
| "X扩展了Y" | extends | GPT-4扩展了GPT-3 |
| "X实现了Y" | implements | BERT实现了预训练 |
| "X与Y相反"、"X矛盾Y" | contradicts | 集中式与分布式矛盾 |

写入L3 frontmatter：
\```yaml
relationships:
  - target: "[[attention-mechanism]]"
    type: derived_from
  - target: "[[lstm]]"
    type: replaces
\```
```

**步骤5：图谱分析增强**

修改 `0100-wiki-meta/scripts/analyze-graph.py`，增加关系分析：

```python
def analyze_typed_relationships():
    """分析类型化关系模式"""
    conn = sqlite3.connect('.wiki.db')
    cur = conn.cursor()
    
    # 1. 最常被uses的概念 → 基础组件
    cur.execute("""
        SELECT target_path, COUNT(*) as usage_count
        FROM relationships
        WHERE rel_type = 'uses' AND target_path IS NOT NULL
        GROUP BY target_path
        ORDER BY usage_count DESC
        LIMIT 10
    """)
    print("=== 最常被使用的基础组件 ===")
    for path, count in cur.fetchall():
        print(f"  {count}x ← {path}")
    
    # 2. 技术演进链（replaces关系）
    cur.execute("""
        SELECT source_path, target_path
        FROM relationships
        WHERE rel_type = 'replaces'
    """)
    print("\n=== 技术演进链（X替代Y）===")
    for src, tgt in cur.fetchall():
        print(f"  {src} → {tgt}")
    
    # 3. 对立概念对（contradicts关系）
    cur.execute("""
        SELECT source_path, target_path
        FROM relationships
        WHERE rel_type = 'contradicts'
    """)
    print("\n=== 对立概念对 ===")
    for src, tgt in cur.fetchall():
        print(f"  {src} ⚔ {tgt}")
    
    conn.close()
```

**验收标准**：
- [ ] schema.yaml包含relationships字段定义
- [ ] SQLite创建了relationships表及索引
- [ ] index-notes.py可提取并索引关系
- [ ] skill-ingest.md包含关系识别规则
- [ ] analyze-graph.py可生成关系分析报告
- [ ] 通过测试：创建带relationships的L3，验证索引和查询

---

## P2 - 可选增强

### E1: 图谱分析工具

**价值**：发现知识孤岛、识别枢纽概念、优化知识连接。

**功能设计**：

创建 `0100-wiki-meta/scripts/analyze-graph.py`：

```python
#!/usr/bin/env python3
"""知识图谱分析工具"""
import sqlite3
from collections import Counter, defaultdict

def analyze_graph():
    conn = sqlite3.connect('.wiki.db')
    cur = conn.cursor()
    
    # 1. Hub分析（入链最多的页面）
    cur.execute("""
        SELECT target_path, COUNT(*) as inbound
        FROM wikilinks
        WHERE target_path IS NOT NULL
        GROUP BY target_path
        ORDER BY inbound DESC
        LIMIT 10
    """)
    print("=== Top 10 Hub页面（入链最多）===")
    for path, count in cur.fetchall():
        print(f"  {count} ← {path}")
    
    # 2. Bridge分析（连接不同topic的页面）
    # 实现逻辑：查询引用多个不同topic的页面
    
    # 3. Dead End分析（无出链的页面）
    cur.execute("""
        SELECT n.path, n.title
        FROM notes n
        LEFT JOIN wikilinks w ON n.path = w.source_path
        WHERE w.id IS NULL AND n.layer IN ('L2', 'L3')
    """)
    print("\n=== Dead End页面（无出链）===")
    for path, title in cur.fetchall():
        print(f"  {title} ({path})")
    
    conn.close()

# 更多分析：社区检测、PageRank等
```

**验收标准**：
- [ ] 生成Hub/Bridge/Dead End报告
- [ ] 输出可操作的优化建议

---

### E2: 批量操作CLI

**价值**：提升运维效率，减少重复手工操作。

**功能设计**：

创建 `0100-wiki-meta/scripts/batch-ops.py`：

```python
#!/usr/bin/env python3
"""批量操作CLI工具"""
import sys, argparse

def batch_update_tags(files: list, add_tags: list, remove_tags: list):
    """批量修改tags"""
    for file in files:
        # 读取frontmatter，修改tags，写回
        pass

def batch_update_status(files: list, new_status: str):
    """批量修改status（draft→published）"""
    pass

def batch_move_to_trash(files: list):
    """批量归档到.trash/"""
    pass

# CLI入口
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--update-tags', nargs='+')
    parser.add_argument('--update-status', choices=['draft', 'published'])
    parser.add_argument('--trash', action='store_true')
    args = parser.parse_args()
    # 实现逻辑
```

**使用示例**：
```bash
# 批量添加tag
python batch-ops.py --update-tags +new-tag file1.md file2.md

# 批量改状态
python batch-ops.py --update-status published 3000-Agent/*.md

# 批量归档
python batch-ops.py --trash old-draft-*.md
```

**验收标准**：
- [ ] 支持批量修改tags/status
- [ ] 支持批量归档
- [ ] 所有操作记录到0109-log/

---

### E3: 使用文档

**价值**：降低新用户上手门槛，规范化操作流程。

**文档结构**：

创建 `docs/user-guide/README.md`：

```markdown
# Mnemosyne 使用指南

## 快速开始

### 1. 初始化
```bash
python 0100-wiki-meta/scripts/init-db.py
python 0100-wiki-meta/scripts/index-notes.py
```

### 2. 摄入新内容
将文件放入 `0003-inbox/`，然后：
```bash
# Claude Code中 @ 引用文件
# 自动执行：标准化 → 生成L2 → 派生L3
```

### 3. 查询
```bash
# FTS5全文搜索
python 0100-wiki-meta/scripts/query.py "keyword"

# 查看统计
python 0100-wiki-meta/scripts/query.py --stats

# 查看死链
python 0100-wiki-meta/scripts/query.py --dead-links
```

### 4. 健康检查
```bash
bash 0100-wiki-meta/scripts/run-lint.sh
```

## 常见操作

### 修复死链
1. 生成死链报告
2. 逐个检查并修复
3. 重新索引

### 归档过期内容
```bash
git mv {file} .trash/
python 0100-wiki-meta/scripts/index-notes.py
```

## 目录结构说明

详见 `CLAUDE.md § 目录结构`
```

**验收标准**：
- [ ] 覆盖初始化、摄入、查询、维护全流程
- [ ] 包含常见问题排查
- [ ] 提供示例和最佳实践

---

### E6: 批量并行优化（新增，来自obsidian-wiki）

**价值**：提升批量摄入效率2-3倍，自动化批次规划，减少人工决策负荷。

**obsidian-wiki实现要点**：
- `batch-plan`命令自动计算最优批次
- 按文件大小和主题聚类分组
- 并行subagent调度执行

**Mnemosyne适配方案**：

**步骤1：创建batch-plan.py**

创建 `0100-wiki-meta/scripts/batch-plan.py`：

```python
#!/usr/bin/env python3
"""批量摄入自动规划工具"""
import sys, os, re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

WIKI_ROOT = Path(__file__).parent.parent.parent
MAX_BATCH_SIZE = 3  # 每批最多文件数
MAX_BATCH_BYTES = 500_000  # 每批最大字节数（约500KB）

def extract_keywords(file_path: Path) -> set[str]:
    """提取文件关键词（用于主题聚类）"""
    try:
        text = file_path.read_text(encoding='utf-8')
        # 简单实现：提取文件名中的关键词
        name = file_path.stem.lower()
        keywords = set(re.findall(r'[a-z]{3,}', name))
        
        # 从内容提取高频词（前10个）
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        word_freq = defaultdict(int)
        for w in words[:500]:  # 只看前500词
            word_freq[w] += 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords.update([w for w, _ in top_words])
        
        return keywords
    except Exception:
        return set()

def calculate_similarity(keywords1: set, keywords2: set) -> float:
    """计算两个文件的主题相似度（Jaccard系数）"""
    if not keywords1 or not keywords2:
        return 0.0
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    return intersection / union if union > 0 else 0.0

def cluster_files(files: List[Path]) -> List[List[Path]]:
    """按主题相似度聚类文件"""
    if len(files) <= 1:
        return [files]
    
    # 提取每个文件的关键词
    file_keywords = {f: extract_keywords(f) for f in files}
    
    # 贪心聚类：从第一个文件开始，找相似的组成批次
    clusters = []
    remaining = files.copy()
    
    while remaining:
        current_batch = [remaining.pop(0)]
        current_keywords = file_keywords[current_batch[0]]
        current_size = current_batch[0].stat().st_size
        
        # 尝试添加相似文件到当前批次
        to_remove = []
        for f in remaining:
            if len(current_batch) >= MAX_BATCH_SIZE:
                break
            
            similarity = calculate_similarity(current_keywords, file_keywords[f])
            file_size = f.stat().st_size
            
            # 相似度>0.2且不超过大小限制，加入批次
            if similarity > 0.2 and current_size + file_size < MAX_BATCH_BYTES:
                current_batch.append(f)
                current_size += file_size
                to_remove.append(f)
        
        for f in to_remove:
            remaining.remove(f)
        
        clusters.append(current_batch)
    
    return clusters

def plan_batches(inbox_path: Path) -> Dict:
    """生成批量摄入计划"""
    # 扫描inbox目录
    files = list(inbox_path.glob("*.md"))
    files = [f for f in files if f.is_file()]
    
    if not files:
        return {"batches": [], "stats": {"total": 0, "to_ingest": 0}}
    
    # 聚类分批
    clusters = cluster_files(files)
    
    batches = []
    for i, cluster in enumerate(clusters, 1):
        total_bytes = sum(f.stat().st_size for f in cluster)
        batches.append({
            "batch_id": i,
            "files": [str(f.relative_to(WIKI_ROOT)) for f in cluster],
            "file_count": len(cluster),
            "total_bytes": total_bytes
        })
    
    return {
        "batches": batches,
        "stats": {
            "total": len(files),
            "to_ingest": len(files),
            "batch_count": len(batches)
        }
    }

def main():
    import json
    inbox = WIKI_ROOT / "0003-inbox"
    plan = plan_batches(inbox)
    print(json.dumps(plan, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

**步骤2：集成到skill-ingest.md**

更新批量模式部分：

```markdown
### 批量模式 - 自动规划（更新）

**自动批次规划**：
\```bash
python 0100-wiki-meta/scripts/batch-plan.py
\```

输出示例：
\```json
{
  "batches": [
    {"batch_id": 1, "files": ["agent-loop.md", "agent-tools.md"], "file_count": 2},
    {"batch_id": 2, "files": ["rag-basics.md", "embedding.md"], "file_count": 2},
    {"batch_id": 3, "files": ["dalle.md"], "file_count": 1}
  ],
  "stats": {"total": 5, "batch_count": 3}
}
\```

**用户确认并行执行**：
1. 确认分批方案
2. 并行启动Agent工具：
   - Agent 1: 处理 batch 1
   - Agent 2: 处理 batch 2
   - Agent 3: 处理 batch 3
3. 所有agent完成后，统一执行步骤8-10（索引+日志+commit）
```

**验收标准**：
- [ ] batch-plan.py可按主题聚类文件
- [ ] 生成合理的批次划分（每批2-3文件）
- [ ] 通过测试：准备5个文件，验证聚类效果

---

## 实施计划（更新）

### Phase 2.1: P0 Lint补全（估算3-4小时）

**Week 1 (Day 1-3)**：
- Day 1: L4, L5, L6（结构、文件名、resource_refs）
- Day 2: L7, L8, L9（远程图片、tags、summary）
- Day 3: L10（topic注册）+ 集成测试

**验收**：
- run-lint.sh显示10/10检查项已实现
- 所有检查通过或输出有效警告

### Phase 2.2: P1 运维治理 + 核心增强（估算8-10小时）⭐️

**Week 1-2 (Day 4-7)**：
- Day 4: 修复图片死链（23个）
- Day 5: 修复概念死链（11个）+ 治理孤立页面（2个）
- **Day 6: E4 置信度系统**（schema + skill + lint，3小时）
- **Day 7: E5 关系类型化**（schema + SQLite + index，3小时）

**验收**：
- check-db-health.py显示死链<5，孤立页面=0
- schema.yaml包含confidence和relationships字段
- SQLite包含relationships表
- check-provenance.py可检测置信度问题
- analyze-graph.py可生成关系分析报告

### Phase 2.3: P2 可选增强（估算7-9小时）

**Week 2-3**（可选，按需启动）：
- E1: 图谱分析工具（2小时）
- E2: 批量操作CLI（2小时）
- E3: 使用文档（1-2小时）
- **E6: 批量并行优化**（2小时）
- E7: 代码AST提取（可选，需外部依赖）

**验收**：
- 工具可用，文档完整
- batch-plan.py可生成合理批次

---

## 总结

### 关键改进

1. **质量保障**：10项Lint检查全覆盖 + 置信度跟踪
2. **运维优化**：死链治理，孤立页面消除
3. **知识图谱增强**：关系类型化，支持精确语义分析⭐️
4. **效率提升**：批量并行优化，图谱分析工具
5. **可维护性**：文档完善，降低上手门槛

### 设计决策

| 决策 | 理由 |
|------|------|
| ❌ 不实现index.md | 冗余、一致性风险、不可扩展（Phase 1确认） |
| ✅ SQLite为唯一索引 | 完善、高效、可扩展（Phase 1确认） |
| ✅ Lint优先于增强 | 质量保障优先级最高（Phase 1确认） |
| ✅ **借鉴obsidian-wiki** | **置信度+关系类型化提升到P1（Phase 2新增）** |
| ✅ **核心增强优先** | **知识图谱能力>运维工具>效率优化（Phase 2调整）** |

### 预期收益

**Phase 1基础**：
- ✅ SQLite基础设施完善
- ✅ 增量索引，查询响应<100ms
- ✅ Wikilinks跟踪，死链可检测

**Phase 2增强**：
- **质量**：Lint覆盖率100%，知识可信度可量化
- **知识图谱**：
  - 置信度系统：区分事实与推理，支持可信度过滤
  - 关系类型化：8种语义关系，支持"技术演进"、"对比分析"查询
  - 图谱分析：识别Hub、Bridge、Dead End，优化知识连接
- **效率**：
  - 死链清零（34→<5）
  - 批量并行：摄入效率提升2-3倍
- **体验**：文档完善，上手时间<30分钟

---

## 附录

### A. 工具清单

| 工具 | 功能 | 状态 |
|------|------|------|
| init-db.py | 初始化SQLite | ✅ Phase 1 |
| index-notes.py | 增量索引 | ✅ Phase 1 |
| query.py | 查询接口 | ✅ Phase 1 |
| check-db-health.py | 健康检查 | ✅ Phase 1 |
| check-config-sync.py | 配置同步 | ✅ Phase 1 |
| run-lint.sh | Lint编排 | 🚧 Phase 2 (3/10→11/11) |
| check-l2-structure.py | L2结构检查 | 📋 Phase 2 P0 |
| check-filename-format.py | 文件名格式 | 📋 Phase 2 P0 |
| check-resource-refs.py | 图片一致性 | 📋 Phase 2 P0 |
| check-remote-images.py | 远程图片残留 | 📋 Phase 2 P0 |
| check-tags-format.py | Tags格式 | 📋 Phase 2 P0 |
| check-summary-length.py | Summary长度 | 📋 Phase 2 P0 |
| check-topic-registration.py | Topic注册 | 📋 Phase 2 P0 |
| **check-provenance.py** | **置信度检查** | **📋 Phase 2 P1** |
| fix-dead-image-links.py | 修复图片死链 | 📋 Phase 2 P1 |
| analyze-graph.py | 图谱分析 | 📋 Phase 2 P2 |
| batch-ops.py | 批量操作 | 📋 Phase 2 P2 |
| **batch-plan.py** | **批量规划** | **📋 Phase 2 P2** |

### B. 参考资料

- Phase 1 Spec: `docs/superpowers/specs/2026-07-06-mnemosyne-optimization-design.md`
- 系统设计: `CLAUDE.md`
- 配置文件: `0100-wiki-meta/configs/`
- 决策记录: `0100-wiki-meta/DECISIONS.md`

---

**文档结束**

