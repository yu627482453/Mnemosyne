# Mnemosyne — 智能本地 Wiki 系统

> Claude Code 自动加载入口。快速导航 + 架构概览。

## 快速导航

| 我要... | 文档位置 | 说明 |
|---------|----------|------|
| 摄入新内容 | [skill-ingest.md](0100-wiki-meta/scripts/skill-ingest.md) | L1 → L2 → L3 完整流程 |
| 查询知识 | [skill-query.md](0100-wiki-meta/scripts/skill-query.md) | 热缓存 + FTS5 检索 |
| 修改内容 | [skill-update.md](0100-wiki-meta/scripts/skill-update.md) | 三级变更策略 |
| 删除条目 | [skill-remove.md](0100-wiki-meta/scripts/skill-remove.md) | L2 及派生数据清理 |
| 检查健康度 | [skill-lint.md](0100-wiki-meta/scripts/skill-lint.md) | 自动修复 + 报告 |

---

## 系统架构

### 三层设计

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| **L1** 原始数据层 | 未加工素材 | `0003-inbox/` | 临时，标准化后移入 .trash/ |
| **L2** 主题知识层 | 高保真标准化数据（**source of truth**） | `{编号}-{主题名}/` | 主数据层，不可变 |
| **L3** 知识加工层 | L2 派生的 typed wiki | `0101-0105/` | Claude 持续维护 |

**核心原则**：
- 写入：L1 → L2 → L3（单向派生）
- 查询：L3（topic 优先）→ L2 → L1（智能检索）
- **L2 是唯一事实源，L3 不得脱离 L2 自行演化**

### L2 与 L3 的关系

- **L2 按来源组织**（书籍、文章、教程等）
- **L3 按知识域组织**（agent/、rag/、llm-basics/ 等）
- **多对一映射**：一个 L2 可派生多个不同 topic 的 L3
- **回溯机制**：L3 的 `source` 字段指向 L2 路径

---

## 权威配置索引

**配置文件位置**：`0100-wiki-meta/configs/`

| 文件 | 用途 | 操作依赖 |
|------|------|----------|
| **schema.yaml** | Frontmatter 字段校验（硬约束） | ingest, update |
| **topics.yaml** | 主题映射与域级分类 | ingest |
| **tag-vocabulary.yaml** | 受控标签词表 | ingest, lint |
| **lint-rules.yaml** | 健康检查规则定义 | lint |
| **l3-directory-inference.yaml** | L3 目录推荐（基于 tags） | ingest |
| **l3-structure.yaml** | L3 子分类结构定义 | ingest |
| **DECISIONS.md** | 设计决策记录（ADR） | 全局 |
| **.wiki.db** | SQLite 索引（notes/topics 表） | query, lint |

**配置维护脚本**：
- `validate-frontmatter.py` — 落盘前强制校验
- `check-config-sync.py` — ingest 结尾强制运行（退出码非 0 则阻断）
- `init-db.py` / `check-db-health.py` — 数据库初始化与健康检查

---

## Frontmatter 规范

### L2（主题知识层）

```yaml
---
id: <自动生成>
title: "原文标题"
topic: <所属主题>
layer: L2
kind: standard
tags: [5-10个, 无空格, 多词用连字符]
aliases: [别名列表]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: "来源"
source_url: "原文链接"
resource_refs: [本地资源路径]
content_hash: <自动计算>
status: draft | published
summary: "200字以上核心摘要"
---
```

### L3 Concept（概念）

```yaml
---
title: "概念名称"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: YYYY-MM-DD
source: ["../L2路径"]
tags: [标签]
status: draft | published
summary: "200字以上"
---
```

### L3 Entity（实体）

```yaml
---
title: "实体名称"
layer: L3
kind: entity
entity_type: Organization | Product | Project | Paper | Person
processing_path: "AI技术/Agent"
updated: YYYY-MM-DD
source: ["../L2路径"]
tags: [标签]
status: draft | published
summary: "简介"
---
```

### L3 Comparison（对比）

```yaml
---
title: "对比标题"
layer: L3
kind: comparison
processing_path: "AI技术/Agent"
comparison_axis: "对比维度"
lhs: "左侧项"
rhs: "右侧项"
updated: YYYY-MM-DD
source: ["../L2路径"]
tags: [标签]
status: draft | published
summary: "对比摘要"
---
```

**完整字段校验规则**：见 `0100-wiki-meta/configs/schema.yaml`

## 命名规则

### 文件名转换规则

| 字符 | 转换 | 示例 |
|------|------|------|
| 空格 | `-` | `agent loop` → `agent-loop` |
| 点号 | `_`（仅扩展名前的点保留） | `v2.5` → `v2_5` |
| 特殊字符 | `_`（`/ : * ? " < > \| + #`） | `hello?world` → `hello_world` |
| 大小写 | 全小写 | `AgentLoop` → `agent-loop` |

**资源路径规范**：`0001-resource/{topic}/{slug}-{timestamp}.{ext}`  
示例：`0001-resource/3000-Agent/agent-loop-20260625143022.png`

### 语言规范

| 层级 | 规则 | 示例 |
|------|------|------|
| **L2 topic 目录** | `{编号}-{显示名}`，技术术语可英文 | `3000-Agent`、`3001-RAG与检索` |
| **L2/L3 文件名** | 英文 kebab-case 全小写 | `agent-loop.md`、`rag-basics.md` |
| **L3 目录** | 英文 slug 全小写，支持子分类 | `agent/core/`、`product/` |
| **title 字段** | 统一中文（frontmatter） | `title: "Agent 循环机制"` |
| **tags** | 英文 slug，连字符连接 | `agent-loop`、`tool-calling` |
| **processing_path** | `{中文大类}/{topic显示名}` | `AI技术/Agent` |
| **正文** | 统一中文 | 技术术语首次出现可附英文原文 |

---

## L2 正文结构

L2 采用**分区结构**（上半提炼，下半原文）：

```markdown
## 核心提炼
概括本文独有的论证逻辑和上下文关系，不重复 L3 可覆盖的通用概念定义。

## 关键概念
- [[概念1]]
- [[概念2]]

## 原文要点
**第一章**：关键论点
**第二章**：关键论点

## 来源
作者、机构、原文链接、原始文件

---

## 原文笔记
原文中文翻译，保留段落层次；代码块保留核心逻辑（函数签名 + 关键注释），省略标准库调用和环境配置。
```

---

## L3 Kind 判定规则

| Kind | 定义 | 触发条件 |
|------|------|----------|
| **comparison** | 两个及以上独立范式的对比分析 | 含 comparison_axis/lhs/rhs；命名含"vs"；分类框架对比 |
| **entity** | 具体的人/组织/产品/项目/论文 | 可独立搜索的外部实体 |
| **concept** | 机制/模式/方法论 | 不属上述两类的抽象概念 |

**注意**：命名含"vs"或分类框架对比 → comparison，不放 concept

---

## 目录结构

```
{编号}-{主题名}/          # L2（按需创建）
0000-meta/                # 模板/脚本/配置
0001-resource/            # 本地资源（图片/附件）
0003-inbox/               # L1
0101-wiki-topics/         # L3 主题综述（域级）
0102-wiki-concepts/       # L3 概念（按主题域）
  ├── agent/              # Agent 相关概念
  ├── rag/                # RAG 与检索
  ├── llm-basics/         # 大模型基础
  ├── model-training/     # 模型训练
  └── ai-engineering/     # AI 工程化
0103-wiki-entities/       # L3 实体（按 entity_type）
  ├── organization/
  ├── product/
  ├── project/
  ├── paper/
  └── person/
0104-wiki-comparisons/    # L3 对比（按 comparison_axis）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
.trash/                   # 回收站
```

---

## 落盘验收清单

每次操作落盘前必须通过：

- [ ] Frontmatter 字段齐全（schema.yaml）
- [ ] L2 包含核心提炼区 + 原文笔记区
- [ ] tags 5-10 个、无空格、连字符
- [ ] summary ≥ 200 字
- [ ] 图片已落地、resource_refs 1:1、无远程图片残留
- [ ] 文件名符合命名规则
- [ ] 死链已处理（planned_links 记录）
- [ ] 配置同步 — `check-config-sync.py` 退出码 0
- [ ] LOG 文件配置同步项逐项标记 PASS/SKIP/FAIL

---

## Git 规范

| 场景 | 格式 |
|------|------|
| 知识操作 | `wiki: {操作} {文件} — {摘要}` |
| 文档变更 | `docs: {描述}` |

**流程**：用户确认后 `git status → add → commit`  
**⚠️ `git push` 必须单独交用户确认，禁止自行推送。**

---

## 维护脚本索引

**脚本位置**：`0100-wiki-meta/scripts/`

### 数据库
- `init-db.py` — 初始化 .wiki.db
- `check-db-health.py` — 数据库健康检查
- `clean-db-records.py` — 清理无效记录

### 校验（必须）
- `validate-frontmatter.py` — Frontmatter 校验（落盘前）
- `check-config-sync.py` — 配置同步校验（ingest 结尾）

### 校验（可选）
11 个 check-*.py 脚本：config-sync、content-hash、db-health、filename-format、l2-structure、planned-links、provenance、remote-images、remove-status、resource-refs、similarity、summary-length、tags-format、topic-registration

### 批量操作
- `batch-ops.py` — 批量修改操作
- `batch-plan.py` — 批量操作计划
- `relocate-l3.py` — L3 文件重定位

### 同步与清理
- `sync-tag-vocabulary.py` — 标签词表同步
- `clean-old-trash.py` — 清理旧回收站

---

## 模型约束

- **Lint 和翻译操作使用 Haiku 模型**（成本优化）
- 其他操作使用会话默认模型
