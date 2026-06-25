# skill-lint：健康检查

> 触发：用户要求检查知识库健康状态
> 模型约束：Lint 检查必须使用 Haiku 模型。
> 执行要求：开始前先用 TaskCreate 创建包含各项检查的 tasklist，每完成一项标记。

## 前置：SQLite 自动同步与一致性检查

### 0. SQLite 索引同步
检测到索引过期时自动重建：
```bash
SYNC_FLAG=$(mktemp)
echo "ok" > "$SYNC_FLAG"

# 0.1 文件存在性检查（DB 中的文件是否都存在）
sqlite3 .wiki.db "SELECT path FROM notes;" 2>/dev/null | while read p; do
  if [ ! -f "$p" ]; then
    echo "STALE: $p (文件已删除)"
    echo "stale" >> "$SYNC_FLAG"
  fi
done

# 0.2 索引完整性检查（本地文件是否都已索引）
find . -type f -name "*.md" \( -path "./3000-*" -o -path "./0101-*" -o -path "./0102-*" -o -path "./0103-*" -o -path "./0104-*" \) ! -path "./.trash/*" | sed 's|^\./||' | while read f; do
  COUNT=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM notes WHERE path='$f';" 2>/dev/null)
  if [ "$COUNT" -eq 0 ]; then
    echo "MISSING: $f (未索引)"
    echo "missing" >> "$SYNC_FLAG"
  fi
done

# 0.3 数量检查
LOCAL_COUNT=$(find . -type f -name "*.md" \( -path "./3000-*" -o -path "./0101-*" -o -path "./0102-*" -o -path "./0103-*" -o -path "./0104-*" \) ! -path "./.trash/*" | wc -l | tr -d ' ')
DB_COUNT=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM notes;" 2>/dev/null || echo 0)
if [ "$LOCAL_COUNT" -ne "$DB_COUNT" ]; then
  echo "MISMATCH: 本地($LOCAL_COUNT) ≠ 数据库($DB_COUNT)"
  echo "mismatch" >> "$SYNC_FLAG"
fi

# 0.4 自动同步（检查临时文件行数，>1 行说明有问题）
LINES=$(wc -l < "$SYNC_FLAG" | tr -d ' ')
rm -f "$SYNC_FLAG"

if [ "$LINES" -gt 1 ]; then
  echo "检测到索引不一致，正在同步..."
  python3 0100-wiki-meta/scripts/index-notes.py
  echo "✓ 索引已同步"
else
  echo "✓ 索引一致性检查通过"
fi
```

### 0.5 标签词表同步检查
检查 tag-vocabulary.yaml 与 tags 表是否同步：
```bash
# 统计词表中的标签数
YAML_TAGS=$(python3 -c "import yaml; data=yaml.safe_load(open('0100-wiki-meta/configs/tag-vocabulary.yaml')); print(len([t for t in data.get('vocabulary', []) if 'tag_en' in t]))" 2>/dev/null || echo 0)
DB_TAGS=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM tags;" 2>/dev/null || echo 0)

if [ "$YAML_TAGS" -ne "$DB_TAGS" ]; then
  echo "WARNING: 标签词表($YAML_TAGS) ≠ 数据库($DB_TAGS)，运行 sync-tag-vocabulary.py"
  python3 0100-wiki-meta/scripts/sync-tag-vocabulary.py
fi

# 报告未使用的标签（仅提示，不自动删除）
UNUSED=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM tags WHERE tag NOT IN (SELECT DISTINCT tag FROM note_tags);" 2>/dev/null || echo 0)
[ "$UNUSED" -gt 0 ] && echo "INFO: $UNUSED 个标签未被使用（词表超集，正常现象）"
```

## 自动修复

### 1. 断裂 wikilink
```bash
rg "\[\[[^]]+\]\]" --no-filename --only-matching -I --glob "*.md" ./ | sed 's/^\[\[//;s/\]\]$//' | sed 's/|.*//' | sort -u | while read link; do
  echo "$link" | grep -qE '(\{\{|\.\.\.|\[\[|\^|\$)' && continue
  echo "$link" | grep -q "^0001-resource/" && continue
  slug=$(basename "$link" .md)
  found=$(find . -iname "${slug}.md" -not -path "./.git/*" -not -path "./.trash/*" -not -path "./0000-meta/*" -not -path "./0100-wiki-meta/*" 2>/dev/null)
  [ -z "$found" ] && echo "BROKEN: [[$link]]"
done
```
不存在 → 标记 `<!-- BROKEN: [[目标]] -->`

## 人工确认项

### 2. 孤立页面
```bash
find . -name "*.md" -not -path "./.git/*" -not -path "./.trash/*" -not -path "./0000-meta/*" -not -path "./0100-wiki-meta/*" | while read f; do
  slug=$(basename "$f" .md)
  refs=$(rg -l "\[\[$slug" ./ 2>/dev/null | grep -v "$f")
  [ -z "$refs" ] && echo "ORPHAN: $f"
done
```

### 3. 长期 draft（>30天）
检查 L2 `status: draft` + `updated` 距今天数 >30 → 报告。

### 4. Frontmatter 不完整
按 `schema.yaml` 逐层校验必填字段。Claude 逐字段检查。

### 5. summary 超范围
缺失 → 报告；<200 字 → 报告。

### 6. tags 格式
含空格 → 报告（多词应用连字符）。

### 7. 文件名格式
```bash
find . -name "*.md" -not -path "./.git/*" | while read f; do
  name=$(basename "$f")
  echo "$name" | grep -q " " && echo "SPACE: $f"
done
```

### 8. resource_refs 一致性
`resource_refs` 与正文 `![[...]]` 是否 1:1 对齐。Claude 逐条比对。

### 9. 远程图片残留
```bash
rg "https?://[^)]*\.(png|jpg|jpeg|gif|svg|webp)" --glob "*.md" -l ./
```

### 10. L3 source 失效
提取 L3 `source` → Glob 检查路径是否存在 → 标记 `<!-- STALE: [[路径]] -->`

### 11. content_hash 一致性
```bash
python 0100-wiki-meta/scripts/check-content-hash.py . 2>/dev/null || python3 0100-wiki-meta/scripts/check-content-hash.py . 2>/dev/null
```

### 12. L2 正文结构
检查 L2 文件是否包含核心提炼区和原文笔记区（以 `---` 分隔）。缺失 → 报告。

### 13. planned_links 缺失
检查 L2 正文中的 `[[wikilink]]` 是否都已列入 `planned_links` 或已有对应文件。

### 14. planned_links 释放
如果 `planned_links` 中的页面已经创建，应将其从列表中移除并转为正式 wikilink。
```bash
python 0100-wiki-meta/scripts/check-planned-links.py . 2>/dev/null || python3 0100-wiki-meta/scripts/check-planned-links.py . 2>/dev/null
```

### 15. SQLite 索引完整性（增强版）
```bash
# 原有检查
FILE_COUNT=$(find . -type f -name "*.md" \( -path "./3000-*" -o -path "./0101-*" -o -path "./0102-*" -o -path "./0103-*" -o -path "./0104-*" \) ! -path "./.trash/*" | wc -l | tr -d ' ')
DB_COUNT=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM notes;" 2>/dev/null || echo 0)
[ "$FILE_COUNT" -ne "$DB_COUNT" ] && echo "ERROR: 文件数($FILE_COUNT) ≠ 数据库记录数($DB_COUNT)，需重新索引"

# 新增：双向一致性检查
echo "=== 双向一致性检查 ==="

# 15.1 DB → 文件系统（过时记录）
sqlite3 .wiki.db "SELECT path FROM notes;" 2>/dev/null | while read p; do
  [ ! -f "$p" ] && echo "STALE: $p (文件已删除，DB 记录过时)"
done

# 15.2 文件系统 → DB（缺失索引）
find . -type f -name "*.md" \( -path "./3000-*" -o -path "./0101-*" -o -path "./0102-*" -o -path "./0103-*" -o -path "./0104-*" \) ! -path "./.trash/*" | sed 's|^\./||' | while read f; do
  COUNT=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM notes WHERE path='$f';" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] && echo "MISSING: $f (未索引)"
done
```

### 16. topics 表同步状态
检查 topics 表是否为空。
```bash
TOPIC_COUNT=$(sqlite3 .wiki.db "SELECT COUNT(*) FROM topics;")
[ "$TOPIC_COUNT" -eq 0 ] && echo "WARNING: topics 表为空，运行 index-notes.py 同步"
```

### 17. 孤立标签检查
检查 note_tags 中是否有未在 tags 表登记的标签。
```bash
sqlite3 .wiki.db "SELECT DISTINCT tag FROM note_tags WHERE tag NOT IN (SELECT tag FROM tags);" | while read orphan; do
  [ -n "$orphan" ] && echo "ORPHAN TAG: $orphan (需添加到 tag-vocabulary.yaml)"
done
```

## 提交
```
git add {标记文件} → git commit -m "wiki: Lint — {修复数量}自动, {报告数量}待确认"
```
**`git push` 必须单独交用户确认，禁止自行推送。**
