# LLM Wiki 当前方案

> 状态：当前唯一方案入口
> 更新时间：2026-05-21
> 说明：本文件覆盖 `phase*` 和 `00-*` 过程文档中的旧口径；历史文档仅作为调研和决策过程参考。

## 1. 核心架构

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工原始素材 | `0003-inbox/` | 临时层，完成 L2 标准化后移入 .trash/ |
| L2 主题知识层 | 高保真标准化数据（source of truth） | `{编号}-{主题名}/` | 主数据层，不可变 |
| L3 知识加工层 | L2 派生的 typed wiki | `0101-0104/` | Claude 持续维护 |

- 写入逻辑：L1 → L2 → L3
- 查询逻辑：L3（topic优先）→ L2 → L1
- L3 不得脱离 L2 自行演化

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
├── 0102-wiki-concepts/           # L3 概念（按主题域：大类/主题域/{slug}.md）
├── 0103-wiki-entities/           # L3 实体（按类别：{entity_type}/{slug}.md）
├── 0104-wiki-comparisons/        # L3 对比（按比较轴：{comparison_axis}/{slug}.md）
├── 0105-wiki-base/               # Base 面板
├── 0109-log/                     # 操作日志
└── {编号}-{主题名}/               # L2 主题知识层
```

## 3. 命名与定位

| 对象 | 规则 | 示例 |
|------|------|------|
| 主题目录 | `{4位编号}-{中文主题名}` | `3001-深度学习` |
| L2 条目 | `{slug}.md`，英文优先，重名追加 `-2/-3` | `transformer.md` |
| L3 主题综述 | `0101/{大类}/{主题域}.md` | `0101/AI技术/深度学习.md` |
| L3 概念 | `0102/{大类}/{主题域}/{slug}.md` | `0102/AI技术/深度学习/transformer.md` |
| L3 实体 | `0103/{entity_type}/{slug}.md` | `0103/Products/claude-code.md` |
| L3 对比 | `0104/{comparison_axis}/{slug}.md` | `0104/Execution/sandbox-vs-auto-mode.md` |
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
tags: [NLP, attention-mechanism, LLM, deep-learning, transformer]
aliases: [transformer, 变换器]
created: 2026-05-20
updated: 2026-05-20
source: paper
source_url: "https://arxiv.org/abs/1706.03762"
resource_refs: []
status: draft
summary: "基于自注意力机制的序列建模架构，2017年由Google在Attention Is All You Need中提出。核心创新是完全摒弃RNN和CNN，通过多头自注意力机制实现并行计算和长距离依赖建模。被BERT、GPT等后续模型广泛采用，是当前LLM的基础架构。适用于需要处理序列数据、捕捉全局依赖的NLP任务。"
---
```

### L3 概念加工页面（0102）

```yaml
---
title: "Transformer"
layer: L3
kind: concept
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source: [3001-深度学习/transformer.md]
tags: [NLP, attention-mechanism, LLM, deep-learning, transformer]
summary: "长篇综合摘要（200-500字）..."
---
```

### L3 实体档案（0103）

```yaml
---
title: "Claude Code"
layer: L3
kind: entity
entity_type: "Product"
updated: 2026-05-20
source: [3002-LLM/claude-code-auto-mode.md]
tags: [AI, LLM, developer-tools, cli, agent]
summary: "长篇综合摘要（200-500字）..."
---
```

### L3 对比分析（0104）

```yaml
---
title: "sandbox vs skip-permissions vs auto-mode"
layer: L3
kind: comparison
comparison_axis: "Execution"
lhs: "sandbox"
rhs: "skip-permissions"
updated: 2026-05-20
source: [3002-LLM/claude-code-auto-mode.md]
tags: [AI, security, permission-model, agent, execution]
summary: "长篇综合摘要（200-500字）..."
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

> L2 必填字段：title, topic, layer, kind, tags(5-10), created, updated, status, summary(200-500字)。
> L3 必填字段：title, layer, kind, updated, summary(200-500字)。
> entity 附加 entity_type；comparison 附加 comparison_axis/lhs/rhs。
> L3 不使用 `created`，以 `updated` 代创建时间。
> 完整校验见 `schema.yaml`。

## 5. 模板

| 层级 | 模板 | 用途 |
|------|------|------|
| L1 | `t-inbox.md` | 原始素材记录 |
| L2 | `t-knowledge.md` | L1 标准化后的主题知识（高保真） |
| L3 | `s-topic.md` | 主题综述（0101，域级） |
| L3 | `s-concept.md` | 概念加工（0102，按主题域） |
| L3 | `s-entity.md` | 实体档案（0103，按实体类别） |
| L3 | `s-comparison.md` | 对比分析（0104，按比较轴） |

详细模板可参考 phase2 历史文档，但以本文件与模板实际文件为准。

## 6. 关键工作流

### Ingest：L1 → L2 → L3

1. 素材进入 `0003-inbox/`
2. Claude 读取 L1，判断归属主题目录（首次归档到某域须用户确认）
3. 生成 slug：英文优先，3-5 个推荐选项，`rg --files` 检查重名
4. 按 `t-knowledge.md` 创建 L2 条目（高保真，不过度摘要；默认中文；tags 5-10 无空格连字符；summary 200-500 字；resource_refs + `![[...]]`）
5. tags 优先使用 `tag-vocabulary.yaml`，新增需用户确认
6. 判断 L3 触发：
   - concept → `0102/{大类}/{主题域}/{slug}.md`
   - entity → `0103/{entity_type}/{slug}.md`
   - comparison → `0104/{comparison_axis}/{slug}.md`
   - 同 slug 匹配 → 合并更新（补充、冲突标注、source 追加）
   - 主题域首次有概念 → 新建 `0101/{大类}/{主题域}.md`
7. 死链治理：正式 [[wikilink]] 仅链接已存在页面；未建概念入 `planned_links`
8. 追加 `0109-log/LOG-YYYY-MM-DD.md`
9. 报告结果，询问是否移入回收站 `0003-inbox/.trash/`
10. 落盘前验收清单（见下）
11. 如用户明确要求，再执行 git commit

### Query：L3（topic 优先）→ L2 → L1

1. 优先检索 `0101-wiki-topics/`，找到匹配主题域
2. 概念：域内检索 `0102/{大类}/{主题域}/`
3. 实体：检索 `0103/`（按 entity_type 目录）
4. 对比：检索 `0104/`（按 comparison_axis 目录）
5. L3 不足时回查 L2 主题目录
6. L2 仍不足且 L1 仍保留时，最后回查 `0003-inbox/`
7. 默认读 Top 8 全文；不足时扩大范围并说明检索层级
8. 回答必须引用 `[[wikilink]]` 或文件路径

### Update

1. 用户指定文件路径、标题或 wikilink
2. 判断变更等级（轻微/中等/重大）
3. 重大变更需 Grep wikilink 引用 → 报告受影响文件 → 同步更新 L3 加工页面
4. L3 不允许人工直接编辑内容逻辑（D010）
5. 如用户明确要求，再执行 git commit

### Lint

**自动修复**：断裂 wikilink
**报告**：孤立页面、长期 draft >30 天、Frontmatter 不完整、summary 超范围(200-500)、tags 格式、L3 source 失效、L3 独立事实

### 落盘验收清单

1. frontmatter 字段齐全
2. tags 5-10 个、无空格、多词连字符
3. summary 200-500 字，有独特判断
4. 链接指向正确层级与主题域
5. L3 source 明确
6. resource_refs 与正文 `![[...]]` 对应
7. 死链已处理

## 7. 当前权威与参考文档

- 当前方案入口：`CURRENT.md`
- 决策记录：`DECISIONS.md`
- 待办事项：`TODO.md`
- 历史参考：`phase2/`、`phase3/`（不作为执行依据）

其他 `phase*` 和 `00-*` 文件为历史过程材料，不作为执行依据。
