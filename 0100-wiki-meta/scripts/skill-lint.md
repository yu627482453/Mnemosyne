# skill-lint：健康检查

> 触发：用户要求检查知识库健康状态
> 模型约束：Lint 检查必须使用 Haiku 模型。
> 执行要求：开始前先用 TaskCreate 创建包含各项检查的 tasklist，每完成一项标记。

## 自动修复

### 1. 断裂 wikilink
```bash
rg "\[\[[^]]+\]\]" --only-matching -I ./ | sed 's/\[\[//;s/\]\]//' | sort -u | while read link; do
  target=$(echo "$link" | sed 's/|.*//')
  slug=$(basename "$target" .md)
  found=$(find . -name "${slug}.md" -not -path "./.git/*" -not -path "./.trash/*" 2>/dev/null)
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
缺失 → 报告；<200 或 >500 字 → 报告。

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

### 12. planned_links 缺失
n### 13. planned_links 释放
如果 `planned_links` 中的页面已经创建，应将其从列表中移除并转为正式 wikilink。
```bash
python 0100-wiki-meta/scripts/check-planned-links.py . 2>/dev/null || python3 0100-wiki-meta/scripts/check-planned-links.py . 2>/dev/null
```

## 提交
```
git add {标记文件} → git commit -m "wiki: Lint — {修复数量}自动, {报告数量}待确认" → git push
```
