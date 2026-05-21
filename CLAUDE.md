# Mnemosyne — 智能本地 Wiki 系统

> Claude Code 自动加载入口。每次会话启动时生效。

## 系统概述

基于 Obsidian + Claude Code 的知识管理系统。三层架构：

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工原始素材 | `0003-inbox/` | 临时，完成 L2 标准化后移入 .trash/ |
| L2 主题知识层 | L1 的标准化数据 | `{编号}-{主题名}/` | 主数据层，不可变（摄入后不改） |
| L3 知识加工层 | L2 综合后的知识成品 | `0101-0104/` | Claude 持续维护 |

- 写入：L1 → L2 → L3
- 查询：L3（topic 优先）→ L2 → L1
- 定位：路径 + slug 文件名，无数字 ID

## 权威配置

| 文件 | 用途 |
|------|------|
| `0000-meta/llm-wiki/CURRENT.md` | 方案入口 |
| `0000-meta/llm-wiki/DECISIONS.md` | 决策记录 |
| `0000-meta/0003-configs/schema.yaml` | 字段校验 |
| `0000-meta/0003-configs/topics.yaml` | 主题映射 |
| `0000-meta/0003-configs/tag-vocabulary.yaml` | 标签参考索引 |
| `0000-meta/0003-configs/lint-rules.yaml` | 健康检查 |

## Frontmatter（摘要）

**L2** — title, topic, layer:L2, kind:standard, tags(3-10), aliases, created, updated, source(manual/url/file/claude), source_url, status(draft/published), summary(≤80字)

**L3** — title, layer:L3, kind(topic/concept/entity/comparison), processing_path("大类/主题域"), updated, source([L2路径列表]), tags, status, summary

**L1** — title, date, source, source_url, status(raw/processing/archived)

> 完整校验见 schema.yaml。L3 无 created，以 updated 代替。

## 目录结构

```
{编号}-{主题名}/          # L2（按需创建）
0000-meta/                # 模板/脚本/配置
0003-inbox/               # L1（含 .trash/）
0101-wiki-topics/         # L3 主题综述（域级：大类/主题域.md）
0102-wiki-concepts/       # L3 概念加工（概念级：大类/主题域/{slug}.md）
0103-wiki-entities/       # L3 实体档案（按需创建）
0104-wiki-comparisons/    # L3 对比分析（按需创建）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
```

## 四操作规范

### Ingest（L1 → L2 → L3）

1. 用户 @ 引用 inbox 文件 → 读取内容
2. 判断归属主题目录（无则按 topics.yaml 新建）
3. 生成 slug（英文优先，3-5 推荐，rg --files 查重）
5. L3 触发：同 slug 则合并（新信息补充、冲突标注、source 追加）；无则新建概念页；域首次则建 0101 综述
6. 跨主题引用建议（tags 重叠 ≥2 → 加 wikilink）
7. 询问用户确认后执行 LOG、移入 `.trash/`、git commit

### Query（L3 topic 优先 → L2 → L1）

1. rg 0101 找匹配主题域 → 提取 processing_path
2. 域内 rg 0102-0104/{大类}/{主题域}/
3. 无匹配 → 全局 rg 0102-0104 → L2 → L1
4. Top 8 全文，不足扩大，标注检索层级
5. 回答引用 [[wikilink]]

### Update（三级变更）

| 等级 | 触发 | 动作 |
|------|------|------|
| 轻微 | 措辞/错别字 | 改正文 → updated → LOG |
| 中等 | tags/aliases | 改 Frontmatter → LOG |
| 重大 | title/summary/事实 | 改内容 → rg 搜索 wikilink 引用 → rg 搜索 L3 source 引用 → 同步更新 → LOG |

L3 不可人工直接编辑内容逻辑；仅允许错别字或格式微调（D010）。

### Lint

自动修复：断裂 wikilink
报告：孤立页面、draft>30天、Frontmatter 不完整、summary 超长/缺失、L3 source 失效

## Git

| 场景 | 格式 |
|------|------|
| 知识操作 | `wiki: {操作} {文件} — {摘要}` |
| 文档变更 | `docs: {描述}` |

提交粒度：Ingest（知识+LOG）、Update（知识+LOG+L3）、Lint（标记文件）
流程：如用户明确要求，再执行 `git status → add → commit → push`，push 失败通知用户
