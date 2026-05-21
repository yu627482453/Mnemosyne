# skill-update：知识更新

> 触发：用户指定文件路径、标题或 wikilink，要求修改已有知识
>
> 执行任何实际修改前，先向用户确认是否需要落盘。

## 前置检查

1. 定位目标文件：通过路径 / Glob 标题 / 解析 wikilink 找到文件
2. 读取当前内容（Frontmatter + 正文）
3. 确认 `layer` 层级（L2 或 L3）
4. 若目标为 L3 → 默认不直接改内容逻辑，仅允许错别字或格式微调；逻辑修改应回到 L2 驱动更新

## 变更分级

### 轻微变更

**触发条件**：正文措辞修正、错别字、格式调整

执行：
1. 修改正文
2. 更新 `updated` 日期
3. 追加 LOG
4. 如用户明确要求，再执行 git commit

### 中等变更

**触发条件**：`tags` / `aliases` 增删改

执行：
1. 修改 Frontmatter 对应字段
2. 更新 `updated` 日期
3. 追加 LOG
4. 如用户明确要求，再执行 git commit

### 重大变更

**触发条件**：`title` 重命名 / `summary` 重写 / 核心事实变更

执行：
1. 先输出受影响范围和最小改动建议，不默认执行批量更新
2. 修改正文和/或 Frontmatter
3. 更新 `updated` 日期
4. **Grep 搜索所有引用本知识的 `[[wikilink]]`**：
   ```
   rg -l "\[\[{slug}\]\]" ./
   ```
4. 列出受影响文件清单，请用户确认
5. 用户确认后更新受影响文件的引用
6. **同步更新 L3 加工页面**：
   ```
   rg -l "{slug}.md" 0101-wiki-topics/ 0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/
   ```
   对每个匹配的 L3 页面，更新 source 列表和关联正文
7. 追加 LOG
8. 如用户明确要求，再执行 git commit

## L3 编辑限制（D010）

- L3 页面为 Claude 加工产出，不允许人工直接编辑
- 允许的修改：错别字、格式微调
- 不允许的修改：改变 wikilink 连接、重写内容结构、删除条目引用
- 若用户坚持修改 L3 内容逻辑 → 回到 Ingest 流程，通过修改 L2 源知识触发 L3 重建

## 提交

如用户明确要求，再执行：

```
git add {变更文件} → git commit -m "wiki: Update {文件名} — {变更摘要}" → git push
```

push 失败则通知用户手动操作。