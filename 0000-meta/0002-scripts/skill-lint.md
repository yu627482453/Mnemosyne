# skill-lint：健康检查

> 触发：用户要求检查知识库健康状态

## 自动修复

执行以下检查并自动修复（无需用户确认）：

### 1. 断裂 wikilink
```
rg "\[\[[^]]+\]\]" --only-matching -I ./ → 提取所有 wikilink 目标
Glob 检查目标 .md 是否存在
不存在 → 在源文件中标记 <!-- BROKEN: [[目标]] -->
```

## 人工确认项

以下问题仅报告，由用户决定是否处理：

### 2. 孤立页面
检查方式：Glob 所有 .md（排除 inbox/templates/configs），Grep 是否有其他文件 `[[链接到它]]`
- 无 incoming link → 报告为孤立页面

### 3. 长期 draft
检查方式：Grep `status: draft` 的 L2 文件，计算 `updated` 距今天数
- >30 天 → 报告，建议 publish 或清理

### 4. Frontmatter 不完整
按 `0000-meta/0003-configs/schema.yaml` 逐层校验：
- L2 缺少必填字段（title/topic/layer/kind/created/updated/status/summary）→ 报告
- L3 缺少必填字段（title/layer/kind/processing_path/updated）→ 报告

### 5. summary 问题
- summary 缺失 → 报告
- summary >80 字符 → 报告
- summary 与正文内容明显不符 → 报告（Claude 判断）

### 6. 跨主题引用建议
对每个 L2 文件，检查 tags 重叠的其他主题目录文件
- 存在重叠但无 wikilink 连接 → 建议建立关联

## 提交

```
git add {标记文件} → git commit -m "wiki: Lint — {修复数量}自动, {报告数量}待确认" → git push
```
