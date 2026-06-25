# skill-query：知识检索（SQLite 索引优先）

> 执行要求：使用 SQLite FTS5 全文索引快速检索，ripgrep 作为回退方案。

> 触发：用户用自然语言提问

## 执行步骤

### 1. SQLite 检索（优先）

```bash
python "D:\obsidian\0100-wiki-meta\scripts\query.py" "关键词" 8
```

自动执行 L3 topic → L3 concept/entity/comparison → L2 → L1 优先级检索。

### 2. ripgrep 回退（索引失效时）

如果 SQLite 返回空：

rg -i "关键词" 0101-wiki-topics/
```

域内检索：
```
rg -i "关键词" 0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/
```

全局回退 L2：
```
rg -i --max-count 5 "关键词" {编号}-{主题名}/
```

回退 L1：
```
rg -i --max-count 5 "关键词" 0003-inbox/
```

### 3. 阅读与排序

- Top 8 全文，优先 L3 > L2 > L1
- 标注检索层级

### 4. 整理回答

- 引用 `[[wikilink]]` 或文件路径
- 标注来源层级
- 信息矛盾时指出

## 约束

- 不确定时明确说"知识库中尚无此信息"
- 单次最多读 15 篇
