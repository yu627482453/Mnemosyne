# Mnemosyne — 智能本地 Wiki 系统

> Claude Code 自动加载入口。

## 系统概述

三层架构，L2 是唯一事实源，L3 由 L2 派生：

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工素材 | `0003-inbox/` | 临时，完成标准化后移入 .trash/ |
| L2 主题知识层 | 高保真标准化数据（source of truth） | `{编号}-{主题名}/` | 主数据层，不可变 |
| L3 知识加工层 | L2 派生的 typed wiki | `0101-0104/` | Claude 持续维护 |

- 写入：L1 → L2 → L3
- 查询：L3（topic 优先）→ L2 → L1
- L3 不得脱离 L2 自行演化

## 权威配置

| 文件 | 用途 |
|------|------|
| `0100-wiki-meta/configs/schema.yaml` | 字段校验 |
| `0100-wiki-meta/configs/topics.yaml` | 主题映射 |
| `0100-wiki-meta/configs/tag-vocabulary.yaml` | 受控标签词表 |
| `0100-wiki-meta/configs/lint-rules.yaml` | 健康检查 |
| `0100-wiki-meta/DECISIONS.md` | 设计决策记录 |
| `0100-wiki-meta/scripts/skill-ingest.md` | 摄入流程 |
| `0100-wiki-meta/scripts/skill-lint.md` | 检查流程 |
| `0100-wiki-meta/scripts/validate-frontmatter.py` | Frontmatter 校验脚本 |

## Frontmatter（摘要）

**L2** — id, title, topic, layer:L2, kind:standard, tags(5-10, 无空格, 多词连字符), aliases, created, updated, source, source_url, resource_refs, content_hash, status(draft/published), summary(200字以上)

**L3 concept** — title, layer:L3, kind:concept, processing_path, updated, source([L2路径]), tags, status, summary(200字以上)

**L3 entity** — title, layer:L3, kind:entity, entity_type(Organization/Product/Project/Paper/Person), processing_path, updated, source, tags, status, summary

**L3 comparison** — title, layer:L3, kind:comparison, processing_path, comparison_axis, lhs, rhs, updated, source, tags, status, summary

**L1** — title, date, source, source_url, status(raw/processing/archived)

> 完整校验见 schema.yaml。

## 命名规则

- 文件名禁止空格 → 空格统一转 `-`
- 文件名主体中的 `.` → 转 `_`（仅最后一个 `.` 是扩展名）
- slug 仅用于路径定位，不替代标题；L2 title 保留原始标题
- 图片资源：`0001-resource/{topic}/{slug}/{timeStamp}.{ext}`（`{topic}` 必须是完整目录名如 `3000-Agent`，非缩写）

### 语言规范

| 层级 | 规则 | 示例 |
|------|------|------|
| L2 topic 目录 | `{编号}-{显示名}`，技术术语可英文 | `3000-Agent`、`3001-RAG与检索` |
| L3 concept 目录 | 英文 slug | `agent/`、`llm-basics/`、`model-training/` |
| L3 concept 文件名 | 英文 kebab-case，专有名词保留原形 | `agent-loop.md`、`CLIP.md`、`ReAct.md` |
| L3 topic 页面 | 显示名，中英文均可 | `Agent.md`、`RAG与检索.md` |
| tags | 默认英文 slug；仅无通用英文对应的学科名用中文 | ✓ 机器学习、✓ agent-loop ✗ 注意力机制（用 attention） |
| processing_path | `{中文大类}/{topic显示名}` | `AI技术/LLM基础`、`AI技术/Agent` |
| 正文 | 统一中文 | 技术术语首次出现可附英文原文 |

### L2 与 L3 的关系

L2 按**来源**组织，L3 按**知识域**组织，两者是多对一映射：

- 一个 L2 文件可派生多个不同 topic 的 L3 concept
- L3 `source` 字段指向 L2 路径，用于回溯
- L2 目录不需要与 L3 目录对齐

示例：`hello-agents-ch3-llm-basics.md`（L2, `3000-Agent/`）→ `transformer-architecture.md`（L3, `llm-basics/`）

## 目录结构

```
{编号}-{主题名}/          # L2（按需创建）
0000-meta/                # 模板/脚本/配置
0001-resource/            # 本地资源（图片/附件）
0003-inbox/               # L1
0101-wiki-topics/         # L3 主题综述（域级）
0102-wiki-concepts/       # L3 概念（按主题域：agent/、rag/、image-generation/、llm-basics/、model-training/、ai-engineering/）
0103-wiki-entities/       # L3 实体（按 entity_type）
0104-wiki-comparisons/    # L3 对比（按 comparison_axis）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
.trash/                   # 回收站
```

## L2 正文结构

L2 正文采用分区结构，上半为提炼，下半为原文：

1. **核心提炼** — 用自己的话概括本文核心观点
2. **关键概念** — 本文涉及的重要概念 wikilink 列表
3. **原文要点** — 章节大纲 + 关键论点，非全文搬运
4. **来源** — 作者、机构、原文链接、原始文件
5. `---` 分隔线
6. **原文笔记** — 原文中文翻译，保留段落层次

## 四操作规范

### Ingest（L1 → L2 → L3）

0. 拆分检查（详见 skill-ingest.md 步骤 0）
1. 用户 @ 引用 inbox → 读取 → 扫描图片
2. 判断归属主题目录（须用户确认）
3. 生成 slug（英文优先，3-5 推荐）；文件名按命名规则处理
4. 图片落地：下载 → `0001-resource/{topic（完整目录名）}/{slug}/{timeStamp}.{ext}` → 改写正文 → 写入 resource_refs
5. 创建 L2：标题保留原文；正文采用分区结构（上半：核心提炼 + 关键概念 + 原文要点 + 来源；下半：原文笔记）
6. L3 触发：逐个检查可派生的 concept/entity/comparison，对每个给出推荐：
   - 是否建 L3（满足其一：独立机制 / 跨源引用≥2 / 工具价值）
   - processing_path 及所属目录（推荐 topic 及理由）
   不建 L3：教科书分类列举、纯对比关系（→ comparison）、已有概念的子细节（→ 合入已有 concept）
   交由用户确认后落盘。一个 L2 可派生多个不同 topic 的 L3。
7. 写入前强制校验：topic/tags/summary/source/processing_path（schema.yaml 硬约束，不过不得落盘）
8. 死链治理（断裂wikilink正常用+planned_links）+ 跨主题引用 + 更新 config
9. LOG + .trash/ + git commit

### Query（L3 topic 优先 → L2 → L1）

1. rg 0101 找主题域 → 域内 rg 0102-0104
2. 无匹配 → 全局 rg → L2 → L1
3. Top 8 全文，引用 [[wikilink]]

### Update（三级变更）

| 等级 | 触发 | 动作 |
|------|------|------|
| 轻微 | 措辞/错别字 | 改正文 → updated → LOG |
| 中等 | tags/aliases | 改 Frontmatter → LOG |
| 重大 | title/summary/事实 | 改内容 → rg wikilink → rg L3 source → 同步 → LOG |

L3 不可人工编辑（D010）。

### Lint

> 模型约束：Lint 和翻译操作使用 Haiku 模型。
自动修复：断裂 wikilink
报告：L2 缺核心提炼区或原文笔记区、孤立页面、draft>30天、Frontmatter 不完整、summary 超范围、tags 格式、文件名格式、resource_refs 不一致、远程图片残留、L3 source 失效、L3 独立事实

## 落盘验收清单

1. frontmatter 字段齐全
2. L2 包含核心提炼区 + 原文笔记区
3. tags 5-10、无空格、连字符
4. summary ≥ 200 字
5. 图片已落地、resource_refs 1:1、无远程图片残留
6. entity/comparison 已主动检查
7. 文件名符合命名规则
8. 死链已处理

## Git

| 场景 | 格式 |
|------|------|
| 知识操作 | `wiki: {操作} {文件} — {摘要}` |
| 文档变更 | `docs: {描述}` |

流程：用户确认后 `git status → add → commit`
**`git push` 必须单独交用户确认，禁止自行推送。**
