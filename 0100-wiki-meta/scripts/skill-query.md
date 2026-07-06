# skill-query：知识检索

> L3 topic 优先 → L2 → L1 分层检索，优先读取 hot.md 热缓存

## 触发方式

用户询问："XX 是什么？"、"查询 XX"、"wiki 中有关于 XX 的内容吗？"

## 检索流程

### 步骤 1：读取热缓存

**优先读取 hot.md**：
```bash
cat 0100-wiki-meta/hot.md
```

如果热缓存中有相关线索，直接跳转到提到的页面，节省 60%+ token。

### 步骤 2：SQLite FTS5 检索（优先）

优先使用 SQLite 全文检索（FTS5），已实现分层逻辑（L3 topic → L3 concept/entity/comparison → L2 → L1）：

```bash
python "D:\obsidian\0100-wiki-meta\scripts\query.py" "<关键词>" 8
```

返回结果直接包含 layer/title/summary/path，跳过文件系统扫描。

**如果结果为空或不足**，降级到步骤 2b。

### 步骤 2b：rg 兜底检索（FTS5 无匹配时）

当 FTS5 检索无结果或结果不满意时，使用 rg 扫描：

```bash
rg "关键词" 0101-wiki-topics/
rg "关键词" 0102-wiki-concepts/相关主题/
```

### 步骤 3：读取相关页面

找到相关页面后：
1. 先读取 L3 概念页（processing_path 精确定位）
2. 如需更多细节，回溯到 L2（通过 source 字段）
3. 合成回答并引用 wikilink

### 步骤 4：返回结果

**回答格式**：
```
根据 wiki 记录：

[核心回答内容]

参考页面：
- [[概念页1]]（L3）
- [[来源页1]]（L2）

相关主题：3000-Agent
```

## Token 优化策略

| 检索层级 | Token 消耗 | 何时使用 |
|---------|-----------|----------|
| hot.md | ~500 | 优先，72h 内活动 |
| Topic 综述 | ~1000 | 无热缓存线索 |
| L3 概念页 | ~800/页 | 精确匹配 |
| L2 原文 | ~2000/页 | 需要原文细节 |

**优先级**：hot.md > L3 > L2 > L1
