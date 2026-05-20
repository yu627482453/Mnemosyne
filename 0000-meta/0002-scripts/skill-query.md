# skill-query：知识检索（L3 → L2 → L1）

> 触发：用户用自然语言提问，需要从 Wiki 中查找答案

## 执行步骤

### 1. 解析查询

识别查询中的关键概念、主题域、实体名。判断查询类型：
- 概念解释（"什么是 X"）→ 优先 concept 页面
- 主题综述（"X 领域有哪些要点"）→ 优先 topic 页面
- 实体信息（"X 公司/人物"）→ 优先 entity 页面
- 对比分析（"X vs Y"）→ 优先 comparison 页面

### 2. 第一轮：检索 L3 加工层

搜索 `0101-wiki-topics/` `0102-wiki-concepts/` `0103-wiki-entities/` `0104-wiki-comparisons/`：

```
rg -i --max-count 5 "关键词" 0101-wiki-topics/ 0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/
```

搜索范围：Frontmatter 的 `title`、`processing_path`、`summary`，以及正文标题。

### 3. 第二轮：回退 L2 主题知识层

若 L3 未找到足够信息（匹配 <3 篇，或匹配内容不相关）：

```
rg -i --max-count 5 "关键词" {编号}-{主题名}/
```

搜索 Frontmatter 的 `title`、`summary`、`tags`，以及正文。

### 4. 第三轮：回退 L1 原始数据层

若 L2 仍不足且有 inbox 文件保留：

```
rg -i --max-count 5 "关键词" 0003-inbox/
```

### 5. 阅读与排序

- 默认读匹配度最高的 **Top 8** 篇全文
- 证据不足时可扩大范围，但需在回答中说明"已检索到第 N 轮"
- 按相关性排序，优先 L3 加工页 > L2 主题知识 > L1 原始素材

### 6. 整理回答

回答格式要求：
- 先给出直接答案，再展开解释
- 每条关键信息必须附带 `[[wikilink]]` 引用
- 引用时标注来源层级，如 `（来源：[[transformer]]，L2）`
- 若信息来自多篇且存在矛盾，指出并请用户判断

### 7. 可选存档

询问用户是否将本次问答存档到 `0004-outbox/`（默认不存档）。

## 约束

- 不确定时明确说"知识库中尚无此信息"，不编造
- 回答中引用实际文件路径或 wikilink，不给猜测的链接
- 单次查询最多读 15 篇全文（超出则报告并请用户缩小范围）
