# skill-query：知识检索（L3 topic 优先 → L2 → L1）

> 执行要求：开始前先用 TaskCreate 创建检索步骤(1-5轮)的 tasklist，确保多轮检索完整执行。


> 触发：用户用自然语言提问

## 执行步骤

### 1. 解析查询

判断查询类型：
- 概念解释 → 优先 0102 concept
- 主题综述 → 优先 0101 topic
- 实体信息 → 优先 0103 entity
- 对比分析 → 优先 0104 comparison

### 2. 第一轮：检索 0101 topic 综述
> 模型：检索步骤可用 Haiku。

```
rg -i "关键词" 0101-wiki-topics/
```

找到匹配主题域 → 提取 processing_path。

### 3. 第二轮：域内检索

概念按主题域搜索：
```
rg -i "关键词" 0102-wiki-concepts/{大类}/{主题域}/
```

实体按类型搜索（Organization/Product/Project/Paper/Person）：
```
rg -i "关键词" 0103-wiki-entities/
```

对比按轴搜索（Architecture/Execution/Retrieval 等）：
```
rg -i "关键词" 0104-wiki-comparisons/
```

### 4. 第三轮：回退全局检索

0101 无匹配 → 全局 0102-0104

### 5. 第四轮：回退 L2

```
rg -i --max-count 5 "关键词" {编号}-{主题名}/
```

### 6. 第五轮：回退 L1

```
rg -i --max-count 5 "关键词" 0003-inbox/
```

### 7. 阅读与排序

- Top 8 全文，不足扩大，标注检索层级
- 优先 L3 > L2 > L1

### 8. 整理回答

- 引用 `[[wikilink]]` 或文件路径
- 标注来源层级
- 信息矛盾时指出

## 约束

- 不确定时明确说"知识库中尚无此信息"
- 单次最多读 15 篇
