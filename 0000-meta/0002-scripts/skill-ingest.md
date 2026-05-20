# skill-ingest：知识摄入（L1 → L2 → L3）

> 触发：用户 `@` 引用 inbox 文件要求处理

## 前置检查

1. 确认目标文件在 `0003-inbox/` 下且存在
2. 读取全文，提取标题、来源、核心内容

## 执行步骤

### 1. 判断归属主题目录

- 从内容中识别领域（个人生活 / AI技术 / 工作业务 / 通用基础）
- 对照 `0000-meta/0003-configs/topics.yaml` 和 `0100-wiki-meta/INDEX.md`
- 匹配已有主题目录：选择最相关的一个
- 无匹配：按 topics.yaml 规则创建新主题目录
  - 编号 = Glob 同千位已有目录取最大编号 +1
  - 格式：`{4位编号}-{中文主题名}`
  - 在 `0100-wiki-meta/INDEX.md` 中登记
  - 报告用户确认

### 2. 生成 slug（D009）

- 英文优先，从标题生成可读 slug
- 给出 3-5 个推荐选项，格式如下：
  1. `transformer`
  2. `transformer-architecture`
  3. `transformer-model`
- 用 `rg --files "{主题目录}/"` 检查重名
- 重名时自动追加 `-2`、`-3`
- 用户可确认推荐或手动指定

### 3. 创建 L2 标准化主题知识

按 `0000-meta/0001-templates/t-knowledge.md` 模板写入：

```yaml
---
title: "标题"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [tag1, tag2, tag3]
aliases: [slug, 中文别名]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: url                # manual | url | file | claude
status: draft
summary: "一句话摘要 ≤80字"
---
```

填写规则：
- `tags`：3-10 个，优先用 `tag-vocabulary.yaml` 已有标签；新增标签需用户确认
- `aliases`：至少包含 slug、中文译名、常见变体
- `summary`：≤80 字，提炼核心要点
- `created` / `updated`：使用当天日期

正文至少包含：核心内容（1-2 段）、要点（3 条以上）、关联（[[wikilink]]）、来源。

### 4. 判断 L3 触发（D004）

对比新知识的 `topic` 与已有 L3 页面的 `processing_path`：

| 情况 | 动作 |
|------|------|
| 匹配已有 processing_path | 追加 `- [[{slug}]] — {summary}` 到对应 L3 页面 |
| L3 页面条目 ≥50 | 自动创建分页 `{主题域}-2.md` |
| 无匹配 processing_path | 在 0101/0102/0103/0104 四个目录下新建 `{大类}/{主题域}.md` |

L3 页面格式见 `CLAUDE.md` L3 Frontmatter 节。

### 5. 追加操作日志

```markdown
| HH:MM:SS | Ingest | {主题目录}/{slug}.md | 新增 {标题} |
```

写入 `0109-log/LOG-YYYY-MM-DD.md`（不存在则创建）。

### 6. 报告与收尾

报告内容：
- 新建文件路径
- 归属主题目录
- 建议关联的已有知识（wikilink 建议）
- 询问："是否删除 inbox 原文件？"（D008：默认删除）

用户确认后 → 删除 L1 原文件 → `git status → git add {文件} → git commit -m "wiki: Ingest {slug}.md — {摘要}" → git push`

## 字段校验（写入前）

对照 `0000-meta/0003-configs/schema.yaml` 的 L2 规则检查全部必填字段。
