# skill-lint：健康检查

> 触发：用户要求检查知识库健康状态

## 自动修复

### 1. 断裂 wikilink
```
rg "\[\[[^]]+\]\]" --only-matching -I ./ → 提取所有 wikilink 目标
Glob 检查目标 .md 是否存在
不存在 → 在源文件中标记 <!-- BROKEN: [[目标]] -->
```

## 人工确认项

### 2. 孤立页面
Glob 所有 .md（排除 inbox/templates/configs），Grep incoming links
- 无 incoming link → 报告

### 3. 长期 draft
Grep `status: draft`，计算 `updated` 距今天数
- >30 天 → 报告

### 4. Frontmatter 不完整
按 `schema.yaml` 逐层校验必填字段

### 5. summary 超范围
- summary 缺失 → 报告
- summary <200 字或 >500 字 → 报告
- summary 是泛定义而非独特判断 → 报告

### 6. tags 格式
- tags 含空格 → 报告（多词应用连字符）
- tags <5 个或 >10 个 → 报告

### 7. L3 source 一致性
提取 L3 `source` 字段 → Glob 检查 L2 路径是否存在
- 不存在 → 标记 `<!-- STALE: [[路径]] -->`

### 8. L3 独立事实
检查 L3 内容是否存在未被 `source` L2 覆盖的事实陈述
- 存在 → 报告建议补充 L2

### 9. 跨主题引用建议
L2 文件 tags 重叠 ≥2 且无 wikilink → 建议关联

## 提交

```
git add {标记文件} → git commit -m "wiki: Lint — {修复}自动, {报告}待确认" → git push
```
