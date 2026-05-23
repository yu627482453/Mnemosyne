# skill-update：知识更新

> 执行要求：开始前先用 TaskCreate 创建变更步骤的 tasklist，确保每步完整执行。


> 触发：用户指定文件路径、标题或 wikilink，要求修改已有知识
> 执行任何实际修改前，先向用户确认是否需要落盘。

## 前置检查

1. 定位目标文件：路径 / Glob 标题 / 解析 wikilink
2. 读取当前内容（Frontmatter + 正文）
3. 确认 `layer` 层级
4. L3 → 默认不直接改内容逻辑，仅允许错别字或格式微调

## 变更分级

### 轻微变更
> 模型：此步骤可用 Haiku。
措辞修正、错别字、格式调整
→ 修改正文 → 更新 updated → LOG → git commit
   - 若修改了正文，更新 `content_hash`: python3 -c "import hashlib; print(hashlib.sha256(open(path,\"rb\").read()).hexdigest()[:8])"

### 中等变更
> 模型：此步骤可用 Haiku。
`tags` / `aliases` 增删改
→ 修改 Frontmatter → 更新 updated → LOG → git commit
   - 若修改了正文，更新 `content_hash`: python3 -c "import hashlib; print(hashlib.sha256(open(path,\"rb\").read()).hexdigest()[:8])"

### 重大变更
`title` 重命名 / `summary` 重写 / 核心事实变更
1. 先输出受影响范围和最小改动建议
2. 修改正文/ Frontmatter
3. 更新 updated
   - 若修改了正文，更新 `content_hash`: python3 -c "import hashlib; print(hashlib.sha256(open(path,\"rb\").read()).hexdigest()[:8])"
4. Grep wikilink 引用：`rg -l "\[\[{slug}\]\]" ./`
5. 列出受影响文件，用户确认
6. 更新受影响文件引用
7. 同步 L3 加工页面（搜索全部 0101-0104 目录下的 source 字段）：
   ```
   rg -l "{slug}.md" 0101-wiki-topics/ 0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/
   ```
8. LOG → git commit

## L3 编辑限制（D010）

- 仅允许错别字、格式微调
- 不得改变 wikilink 连接、内容结构
- 逻辑修改 → 回 L2 驱动更新

## 提交
用户确认后：
```
git add {变更文件} → git commit -m "wiki: Update {文件名} — {变更摘要}" → git push
```
