# LLM Wiki 当前方案

> 状态：当前唯一方案入口
> 更新时间：2026-05-20
> 说明：本文件覆盖 `phase*` 和 `00-*` 过程文档中的旧口径；历史文档仅作为调研和决策过程参考。

## 1. 核心架构

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工原始素材 | `0003-inbox/` | 临时层，完成 L2 标准化后可删除或归档 |
| L2 主题知识层 | L1 的标准化数据，按主题目录存放 | `{编号}-{主题名}/` | 主数据层，保持来源约束和结构统一 |
| L3 知识加工层 | 基于 L2 拆解、重构、聚合后的知识页面 | `0101-0104/` | 加工层，由 Claude 持续维护 |

- 写入逻辑：L1 → L2 → L3
- 查询逻辑：L3 → L2 → L1
- L1 仅在需要追溯原始材料且文件仍保留时使用。

## 2. 当前目录规划

```text
obsidian-vault/
├── 0000-meta/                    # 项目管理
│   ├── 0000-project-docs/
│   ├── 0001-templates/
│   ├── 0002-scripts/
│   ├── 0003-configs/
│   └── llm-wiki/
├── 0001-resource/
├── 0002-example/
├── 0003-inbox/                   # L1 原始数据层
├── 0004-outbox/
├── 0005-markmind/
├── 0006-excalidraw/
├── 0100-wiki-meta/
├── 0101-wiki-topics/             # L3
├── 0102-wiki-concepts/           # L3
├── 0103-wiki-entities/           # L3
├── 0104-wiki-comparisons/        # L3
├── 0105-wiki-base/
├── 0109-log/
├── 0999-other/
└── {编号}-{主题名}/               # L2 主题知识层
```

## 3. 命名与定位

| 对象 | 规则 | 示例 |
|------|------|------|
| 主题目录 | `{4位编号}-{主题名}` | `3001-深度学习` |
| L2 知识条目 | `{slug}.md`，重名追加 `-2/-3` | `transformer.md` |
| L3 加工页面 | `{主题域}.md` | `0102-wiki-concepts/AI技术/深度学习.md` |

单条知识不维护数字 ID，使用“主题目录路径 + slug 文件名”定位。

## 4. Frontmatter

### L2 标准化主题知识

```yaml
---
title: "Transformer"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [NLP, 注意力机制, LLM]
aliases: [transformer, 变换器, 自注意力架构]
created: 2026-05-19
updated: 2026-05-19
source: manual
status: draft
summary: "基于自注意力机制的序列建模架构"
---
```

### L3 加工页面

```yaml
---
title: "深度学习概念索引"
layer: L3
kind: concept
processing_path: "AI技术/深度学习"
updated: 2026-05-19
entry_count: 12
source_topics: [3001-深度学习]
---
```

## 5. 模板

| 层级 | 模板 | 用途 |
|------|------|------|
| L1 | `t-inbox.md` | 原始素材记录 |
| L2 | `t-knowledge.md` | L1 标准化后的主题知识 |
| L3 | `s-topic.md` | 主题综述 |
| L3 | `s-concept.md` | 概念加工 |
| L3 | `s-entity.md` | 实体档案 |
| L3 | `s-comparison.md` | 对比分析 |

详细模板见 `phase2/02-06-模板详细设计.md`。

## 6. 关键工作流

### Ingest：L1 → L2 → L3

1. 原始素材进入 `0003-inbox/`。
2. Claude 读取 L1，判断归属主题目录。
3. 用 `t-knowledge.md` 创建 L2 标准化主题知识。
4. L2 校验通过后，L1 可删除或归档。
5. 根据需要更新 L3 加工页面。
6. 写入 `0109-log/LOG-YYYY-MM-DD.md`。

### Query：L3 → L2 → L1

1. 优先检索 `0101-0104/` L3 加工页面。
2. L3 证据不足时，检索 L2 主题知识目录。
3. L2 仍不足且 L1 文件仍保留时，追溯 `0003-inbox/`。
4. 回答必须引用实际 wikilink 或文件路径。

### Update

1. 用户通过文件路径、标题或 wikilink 指定目标。
2. 更新 L2 时，同步判断是否需要级联更新 L3。
3. 重大事实变化需要报告受影响页面。

## 7. 当前权威文档

- 当前方案入口：`CURRENT.md`
- 决策记录：`DECISIONS.md`
- 待办事项：`TODO.md`
- 模板细节：`phase2/02-06-模板详细设计.md`
- 分类与关联细节：`phase2/02-05-分类与关联方法.md`
- 详细方案草案：`phase3/03-详细方案设计.md`

其他 `phase*` 和 `00-*` 文件为历史过程材料，不作为执行依据。
