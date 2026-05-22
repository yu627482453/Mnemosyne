# LLM Wiki 当前方案

> 状态：当前唯一方案入口
> 更新时间：2026-05-21
> 说明：本文件覆盖 `phase*` 和 `00-*` 过程文档中的旧口径；历史文档仅作为调研和决策过程参考。

## 1. 核心架构

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工原始素材 | `0003-inbox/` | 临时层，完成 L2 标准化后移入 .trash/ |
| L2 主题知识层 | L1 的标准化数据，按主题目录存放 | `{编号}-{主题名}/` | 主数据层，保持来源约束和结构统一 |
| L3 知识加工层 | 基于 L2 拆解、重构、聚合后的知识页面 | `0101-0104/` | 加工层，由 Claude 持续维护 |

- 写入逻辑：L1 → L2 → L3
- 查询逻辑：L3（topic优先）→ L2 → L1
- L1 仅在需要追溯原始材料且文件仍保留时使用。

## 2. 当前目录规划

```text
obsidian-vault/
├── 0000-meta/                    # 项目管理
│   ├── 0001-templates/
│   ├── 0002-scripts/
│   ├── 0003-configs/
│   └── llm-wiki/
├── 0003-inbox/                   # L1 原始数据层
├── 0101-wiki-topics/             # L3 主题综述（域级：大类/主题域.md）
├── 0102-wiki-concepts/           # L3 概念加工（概念级：大类/主题域/{slug}.md）
├── 0103-wiki-entities/           # L3 实体档案（实体级：大类/主题域/{slug}.md）
├── 0104-wiki-comparisons/        # L3 对比分析（对比级：大类/主题域/{slug}.md）
├── 0105-wiki-base/
├── 0109-log/
└── {编号}-{主题名}/               # L2 主题知识层
```

## 3. 命名与定位

| 对象 | 规则 | 示例 |
|------|------|------|
| 主题目录 | `{4位编号}-{中文主题名}` | `3001-深度学习` |
| L2 条目 | `{slug}.md`，英文优先，重名追加 `-2/-3` | `transformer.md` |
| L3 主题综述 | `0101-wiki-topics/{大类}/{主题域}.md` | `0101-wiki-topics/AI技术/深度学习.md` |
| L3 概念/实体/对比 | `010{2-4}/{大类}/{主题域}/{slug}.md` | `0102-wiki-concepts/AI技术/深度学习/transformer.md` |
| 收件箱条目 | `{日期}-{slug}.md` | `2026-05-20-新发现.md` |

单条知识不维护数字 ID，使用"主题目录路径 + slug 文件名"定位。

## 4. Frontmatter

### L2 标准化主题知识

```yaml
---
title: "Transformer"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [NLP, 注意力机制, LLM]
aliases: [transformer, 变换器]
created: 2026-05-20
updated: 2026-05-20
source: manual
source_url: ""
status: draft
summary: "基于自注意力机制的序列建模架构，2017年由Google在Attention Is All You Need中提出。核心创新是完全摒弃RNN和CNN，通过多头自注意力机制实现并行计算和长距离依赖建模。被BERT、GPT等后续模型广泛采用，是当前LLM的基础架构。适用于需要处理序列数据、捕捉全局依赖的NLP任务。"
---
```

### L3 概念加工页面（示例：0102）

```yaml
---
title: "Transformer"
layer: L3
kind: concept
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source: [3001-深度学习/transformer.md]
---
```

### L3 主题综述（示例：0101）

```yaml
---
title: "深度学习主题综述"
layer: L3
kind: topic
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source: [3001-深度学习/transformer.md]
---
```

### L1 Inbox

```yaml
---
title: "标题"
date: 2026-05-20
source: url
source_url: "https://..."
status: raw
---
```

> L2 必填字段：title, topic, layer, kind, created, updated, status, summary。
> L3 必填字段：title, layer, kind, processing_path, updated。
> L3 不使用 `created`，以 `updated` 代创建时间。

## 5. 模板

| 层级 | 模板 | 用途 |
|------|------|------|
| L1 | `t-inbox.md` | 原始素材记录 |
| L2 | `t-knowledge.md` | L1 标准化后的主题知识 |
| L3 | `s-topic.md` | 主题综述（0101，域级） |
| L3 | `s-concept.md` | 概念加工（0102，概念级） |
| L3 | `s-entity.md` | 实体档案（0103，实体级） |
| L3 | `s-comparison.md` | 对比分析（0104，对比级） |

详细模板可参考 `0000-meta/llm-wiki/phase2/02-06-模板详细设计.md`，但以本文件与模板实际文件为准。

## 6. 关键工作流

### Ingest：L1 → L2 → L3

1. 素材进入 `0003-inbox/`
2. Claude 读取 L1，判断归属主题目录
3. 生成 slug：英文优先，3-5 个推荐选项，`rg --files` 检查重名
4. 按 `t-knowledge.md` 创建 L2 条目 `{主题目录}/{slug}.md`
5. tags 优先使用 `tag-vocabulary.yaml` 已有标签，新增需用户确认
6. 判断 L3 触发：
   - 匹配到已有概念页 → 更新该页
   - 无匹配 → 新建概念页 `0102-wiki-concepts/{大类}/{主题域}/{slug}.md`
   - 主题域首次有概念 → 新建主题综述 `0101-wiki-topics/{大类}/{主题域}.md`
7. 询问用户确认后追加 `0109-log/LOG-YYYY-MM-DD.md`
8. 报告结果，询问是否移入回收站 `0003-inbox/.trash/`
9. 如用户明确要求，再执行 git commit

### Query：L3（topic 优先）→ L2 → L1

1. 优先检索 `0101-wiki-topics/`，找到匹配的主题域
2. 在匹配的域内检索 `0102-0104/{大类}/{主题域}/`
3. 若 0101 无匹配 → 全局检索 0102-0104
4. L3 不足时回查 L2 主题目录
5. L2 仍不足且 L1 仍保留时，最后回查 `0003-inbox/`
6. 默认读 Top 8 全文；不足时扩大范围并说明检索层级
7. 回答必须引用 `[[wikilink]]` 或文件路径

### Update

1. 用户指定文件路径、标题或 wikilink
2. 判断变更等级（轻微/中等/重大）
3. 重大变更需 Grep wikilink 引用 → 报告受影响文件 → 同步更新 L3 加工页面
4. L3 不允许人工直接编辑内容逻辑，仅允许错别字或格式类微调
5. 如用户明确要求，再执行 git commit

### Lint（健康检查）

**自动修复**：断裂 wikilink
**报告**：孤立页面、长期 draft >30 天、Frontmatter 不完整、summary 超长或缺失、L3 source 失效

## 7. 当前权威与参考文档

- 当前方案入口：`0000-meta/llm-wiki/CURRENT.md`
- 决策记录：`0000-meta/llm-wiki/DECISIONS.md`
- 待办事项：`0000-meta/llm-wiki/TODO.md`
- 模板细节参考：`0000-meta/llm-wiki/phase2/02-06-模板详细设计.md`（参考，不作为执行依据）
- 分类与关联细节参考：`0000-meta/llm-wiki/phase2/02-05-分类与关联方法.md`（参考，不作为执行依据）
- 详细方案草案参考：`0000-meta/llm-wiki/phase3/03-详细方案设计.md`（参考，不作为执行依据）

其他 `phase*` 和 `00-*` 文件为历史过程材料，不作为执行依据。
