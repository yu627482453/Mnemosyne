# LLM Wiki 当前方案

> 状态：当前唯一方案入口
> 更新时间：2026-05-22
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
├── 0001-resource/                # 本地资源（图片/附件）
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
| 主题目录 | `{4位编号}-{中文主题名}` | `3001-Agent` |
| L2 条目 | 空格转`-`，主体`.`转`_`；英文优先；重名追加 `-2/-3` | `Scaling-Managed-Agents.md` |
| L3 主题综述 | `0101/{大类}/{主题域}.md` | `0101/AI技术/Agent.md` |
| L3 概念 | `0102/{大类}/{主题域}/{slug}.md` | `0102/AI技术/Agent/managed-agents.md` |
| L3 实体 | `0103/{entity_type}/{slug}.md` | `0103/Organizations/anthropic.md` |
| L3 对比 | `0104/{comparison_axis}/{slug}.md` | `0104/Architecture/single-vs-multi-agent.md` |
| 收件箱条目 | `{日期}-{slug}.md` | `2026-05-22-Scaling-Managed-Agents.md` |

slug 仅用于路径定位，不替代标题语义。L2 title 保留原始标题。

## 4. Frontmatter

### L2 标准化主题知识

```yaml
---
title: "Scaling Managed Agents: Decoupling the brain from the hands"
topic: "3001-Agent"
layer: L2
id: "a3f2b1c9"
kind: standard
tags: [AI, LLM, Agent, agent-architecture, context-engineering, infrastructure, overview]
aliases: [managed-agents, 托管代理, 脑手分离架构]
created: 2026-05-22
updated: 2026-05-22
source: url
source_url: "https://www.anthropic.com/engineering/managed-agents"
resource_refs: ["0001-resource/3001-Agent/managed-agents/20260522-143015.png"]
status: draft
summary: "Anthropic 的 Managed Agents 是一种托管式长时间运行代理服务……（200-500字）"
content_hash: "d4e5f6a7"
---
```

### L3 概念加工页面（0102）

```yaml
---
title: "Managed Agents"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3001-Agent/managed-agents.md"]
tags: [AI, LLM, Agent, agent-architecture, context-engineering, infrastructure, overview]
summary: "Managed Agents 是 Anthropic 在 Claude Platform 上提供的托管式代理服务……（200-500字）"
content_hash: "d4e5f6a7"
---
```

### L3 实体档案（0103）

```yaml
---
title: "Anthropic"
layer: L3
kind: entity
entity_type: "Organization"
updated: 2026-05-22
source: ["3001-Agent/managed-agents.md"]
tags: [AI, organization, agent, infrastructure]
summary: "Anthropic 是一家 AI 安全与研究公司……（200-500字）"
content_hash: "d4e5f6a7"
---
```

### L3 对比分析（0104）

```yaml
---
title: "Pets vs Cattle"
layer: L3
kind: comparison
comparison_axis: "Architecture"
lhs: "Pets"
rhs: "Cattle"
updated: 2026-05-22
source: ["3001-Agent/managed-agents.md"]
tags: [infrastructure, architecture, reliability, agent]
summary: "对比有状态 Pet 模式与无状态 Cattle 模式在代理系统中的适用性……（200-500字）"
content_hash: "d4e5f6a7"
---
```

### L1 Inbox

```yaml
---
title: "标题"
date: 2026-05-22
source: url
source_url: "https://..."
status: raw
---
```

> L2 必填字段：title, topic, layer, kind, tags(5-10), created, updated, status, summary(200-500字)。
> L3 必填字段：title, layer, kind, updated, summary(200-500字)。
> entity 附加 entity_type；comparison 附加 comparison_axis/lhs/rhs。
> 完整校验见 `schema.yaml`。

## 5. 模板

| 层级 | 模板 | 用途 |
|------|------|------|
| L1 | `t-inbox.md` | 原始素材记录 |
| L2 | `t-knowledge.md` | L1 标准化后的主题知识（高保真，含原文主体） |
| L3 | `s-topic.md` | 主题综述（0101，域级） |
| L3 | `s-concept.md` | 概念加工（0102，按主题域） |
| L3 | `s-entity.md` | 实体档案（0103，按实体类别） |
| L3 | `s-comparison.md` | 对比分析（0104，按比较轴） |

## 6. 关键工作流

### Ingest：L1 → L2 → L3

1. 素材进入 `0003-inbox/`
2. Claude 读取 L1 + 扫描图片
3. 判断归属主题目录（首次归档须用户确认）
4. 生成 slug + 按命名规则生成文件名（空格→`-`，主体`.`→`_`）
5. 图片落地：下载→`0001-resource/{topic}/{slug}/{timeStamp}.{ext}`→改写正文→resource_refs；**下载失败暂停，通知用户**
6. 按 `t-knowledge.md` 创建 L2（核心内容 + 文章要点 + **原文主体** + 关联 + 来源）
7. L3 触发：concept/entity/comparison **主动逐项检查**
8. 死链治理 + 跨主题引用
9. LOG + .trash/ + git commit

### Query：L3（topic 优先）→ L2 → L1

1. rg 0101 找匹配主题域 → 域内 rg 0102-0104
2. 无匹配 → 全局 rg → L2 → L1
3. Top 8 全文，引用 [[wikilink]]

### Update

1. 用户指定文件路径、标题或 wikilink
2. 判断变更等级（轻微/中等/重大）
3. 重大变更需 Grep wikilink 引用 → 同步 L3
4. L3 不可人工编辑内容逻辑（D010）

### Lint

**自动修复**：断裂 wikilink
**报告**：L2缺原文主体、孤立页面、draft>30天、Frontmatter不完整、summary超范围、tags格式、文件名格式、resource_refs不一致、远程图片残留、L3 source失效、L3独立事实

## 7. 当前权威与参考文档

- 当前方案入口：`CURRENT.md`
- 决策记录：`DECISIONS.md`
- 待办事项：`TODO.md`
- 历史参考：`phase2/`、`phase3/`（不作为执行依据）

其他 `phase*` 和 `00-*` 文件为历史过程材料，不作为执行依据。
