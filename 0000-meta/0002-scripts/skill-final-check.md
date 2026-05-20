# skill-final-check：操作收尾检查

> 触发：每次 Ingest / Update / Lint 操作结束时自动执行

## 检查清单

### 1. 变更文件清单
列出本次操作新增、修改、删除的所有文件：
```
新增：
  - {文件路径}
修改：
  - {文件路径}
删除：
  - {文件路径}
```

### 2. Frontmatter Schema 校验
对新写入或修改的文件，逐层按 `0000-meta/0003-configs/schema.yaml` 校验：

**L2 必填检查**：
- [ ] `title` 非空，≤120 字
- [ ] `topic` 匹配 `^\d{4}-.+$`
- [ ] `layer` = L2
- [ ] `kind` = standard
- [ ] `created` / `updated` 格式 YYYY-MM-DD
- [ ] `status` ∈ {draft, published}
- [ ] `summary` 非空，≤80 字

**L3 必填检查**：
- [ ] `title` 非空
- [ ] `layer` = L3
- [ ] `kind` ∈ {topic, concept, entity, comparison}
- [ ] `processing_path` 匹配 `^\S+/\S+$`
- [ ] `updated` 格式 YYYY-MM-DD

**L1 检查**（仅 inbox）：
- [ ] `status` ∈ {raw, processing, archived}

### 3. wikilink 可解析性
- [ ] 新增的 `[[wikilink]]` 目标文件存在
- [ ] 修改的 `[[wikilink]]` 仍指向有效目标
- [ ] 删除文件后，无其他文件引用其 wikilink（或已标记为 BROKEN）

### 4. LOG 确认
- [ ] 已追加到 `0109-log/LOG-YYYY-MM-DD.md`
- [ ] LOG 格式正确：`| HH:MM:SS | {操作} | {目标} | {摘要} |`

### 5. Git 状态
```
git status
```
- [ ] 无意外修改的文件
- [ ] 无遗漏提交的文件（.tmp/.bak 等应在 .gitignore）
- [ ] 报告未提交变更列表

### 6. 失败恢复
若中途操作失败：
```
已完成：
  - {已完成的步骤}
未完成：
  - {未完成的步骤}
需人工处理：
  - {需要用户介入的事项}
```
不得静默失败。
