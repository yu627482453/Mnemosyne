# Mnemosyne — 智能本地 Wiki 系统

> Claude Code 自动加载入口。每次会话启动时生效。

## 系统概述

基于 Obsidian + Claude Code 的知识管理系统。三层架构：

| 层级 | 定位 | 目录 | 生命周期 |
|------|------|------|----------|
| L1 原始数据层 | 未加工原始素材 | `0003-inbox/` | 临时，完成 L2 标准化后默认删除 |
| L2 主题知识层 | L1 的标准化数据 | `{编号}-{主题名}/` | 主数据层 |
| L3 知识加工层 | L2 拆解重构后的页面 | `0101-0104/` | Claude 持续维护 |

- 写入逻辑：L1 → L2 → L3
- 查询逻辑：L3（topic 优先）→ L2 → L1
- 单条知识不维护数字 ID，使用"主题目录路径 + slug 文件名"定位

## 权威文档入口

执行前先读以下文件（按需，不必全读）：

| 文件 | 用途 | 何时读 |
|------|------|--------|
| `0000-meta/llm-wiki/CURRENT.md` | 当前方案入口 | 首次执行或不确定口径时 |
| `0000-meta/llm-wiki/DECISIONS.md` | 架构决策记录 | 不确定某项选择时 |
| `0000-meta/0003-configs/schema.yaml` | 字段校验规则 | Ingest/Update 写文件时 |
| `0000-meta/0003-configs/topics.yaml` | 主题目录映射 | 新建主题目录时 |
| `0000-meta/0003-configs/tag-vocabulary.yaml` | 受控标签词表 | 写 tags 时 |
| `0000-meta/0003-configs/lint-rules.yaml` | 健康检查规则 | 执行 Lint 时 |

> `0000-meta/llm-wiki/phase*` 和 `00-*` 文件为历史过程文档，不作为执行依据。

## Frontmatter Schema（摘要）

### L2 标准化主题知识

```yaml
title: "标题"
topic: "3001-深度学习"    # 所属主题目录名
layer: L2
kind: standard            # L2 固定值
tags: [tag1, tag2]        # 3-10 个，优先使用 tag-vocabulary.yaml
aliases: [slug, 别名]
created: 2026-05-20
updated: 2026-05-20
source: manual            # manual | url | file | claude
status: draft             # draft | published
summary: "一句话摘要 ≤80字"
```

### L3 加工页面

概念/实体/对比页（0102-0104）：
```yaml
title: "Transformer"
layer: L3
kind: concept             # topic | concept | entity | comparison
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source_topics: [3001-深度学习]
```

主题综述（0101，域级）：
```yaml
title: "深度学习主题综述"
layer: L3
kind: topic
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source_topics: [3001-深度学习]
```

### L1 Inbox

```yaml
title: "标题"
date: 2026-05-20
source: url
source_url: "https://..."
status: raw               # raw → processing → archived/删除
```

> 完整字段定义见 `0100-wiki-meta/SCHEMA.md`，校验规则见 `0000-meta/0003-configs/schema.yaml`。
> L2 必填字段：title, topic, layer, kind, created, updated, status, summary。
> L3 以 updated 代 created，不单独设 created 字段。

## 命名规则

| 对象 | 规则 | 示例 |
|------|------|------|
| 主题目录 | `{4位编号}-{中文主题名}` | `3001-深度学习` |
| L2 条目 | `{slug}.md`，英文优先，重名追加 `-2/-3` | `transformer.md` |
| 收件箱条目 | `{日期}-{slug}.md` | `2026-05-20-新发现.md` |
| L3 主题综述 | `0101/{大类}/{主题域}.md` | `0101/AI技术/深度学习.md` |
| L3 概念/实体/对比 | `010{2-4}/{大类}/{主题域}/{slug}.md` | `0102/AI技术/深度学习/transformer.md` |

slug 生成规则：英文优先，操作时给出 3-5 个推荐选项，用户确认或手动指定。

## 目录结构

```
{编号}-{主题名}/         # L2 主题知识层（按需创建）
├── 0000-meta/
│   ├── 0001-templates/  # 知识模板（Templater）
│   ├── 0002-scripts/    # Skill 文件
│   └── 0003-configs/    # 机器可校验配置
├── 0003-inbox/           # L1 原始数据层
├── 0100-wiki-meta/       # Wiki 元数据
├── 0101-wiki-topics/     # L3 主题综述（域级）
├── 0102-wiki-concepts/   # L3 概念加工（概念级）
├── 0103-wiki-entities/   # L3 实体档案（实体级）
├── 0104-wiki-comparisons/# L3 对比分析（对比级）
├── 0105-wiki-base/       # Base 导航面板
└── 0109-log/             # 操作日志
```

## 四操作规范

### Ingest（L1 → L2 → L3）

1. 素材进入 `0003-inbox/`
2. 用户 `@` 引用 inbox 文件要求处理
3. 读取内容 → 判断归属主题目录 → 不存在则按 topics.yaml 规则新建
4. 生成 slug：英文优先，给出 3-5 个推荐选项，`rg --files` 检查重名
5. 按 `t-knowledge.md` 模板创建 L2 条目 `{主题目录}/{slug}.md`
6. tags 优先使用 `tag-vocabulary.yaml` 已有标签，新增需用户确认
7. 判断 L3 触发：
   - 匹配到已有概念页（同 slug）→ 更新该页
   - 无匹配 → 新建概念页 `0102-wiki-concepts/{大类}/{主题域}/{slug}.md`
   - 若为实体/对比 → 对应写入 0103/0104
   - 主题域首次有内容 → 新建主题综述 `0101-wiki-topics/{大类}/{主题域}.md`
8. 追加 `0109-log/LOG-YYYY-MM-DD.md`
9. 报告结果，询问是否移入回收站 `0003-inbox/.trash/`（默认）
10. git commit

### Query（L3 topic 优先 → L2 → L1）

1. 优先检索 `0101-wiki-topics/`，找到匹配主题域
2. 在匹配域内检索 `0102-0104/{大类}/{主题域}/`
3. 若 0101 无匹配 → 全局检索 0102-0104
4. L3 不足时回查 L2 主题目录
5. L2 仍不足且 L1 仍保留时，最后回查 `0003-inbox/`
6. 默认读 Top 8 全文；不足时扩大范围并在回答中说明检索层级
7. 回答必须引用 `[[wikilink]]` 或文件路径

### Update（三级变更）

1. 用户指定文件路径、标题或 wikilink
2. 判断变更等级：
   - **轻微**（措辞/错别字）：修改正文 → 更新 updated → LOG
   - **中等**（tags/aliases）：修改 Frontmatter → LOG
   - **重大**（title/summary/核心事实）：修改正文/Frontmatter → Grep 搜索 wikilink 引用 → 报告受影响文件 → 用户确认后同步更新 L3 加工页面 → LOG
3. L3 不允许人工直接编辑（最多改错别字，不得改变 wikilink 连接和逻辑）
4. git commit

### Lint（健康检查）

**自动修复**：
- INDEX.md 与实际主题目录不一致 → 更新 INDEX.md
- 内部 `[[wikilink]]` 指向不存在 → 标记

**报告（需人工）**：
- 孤立页面（无 incoming wikilink）
- 长期 draft >30 天
- 缺失跨主题引用建议
- Frontmatter 不完整（按 schema.yaml 校验）
- summary 超长或缺失

## Git 提交规范

| 场景 | 格式 |
|------|------|
| Claude 知识操作 | `wiki: {操作} {文件名} — {摘要}` |
| 项目文档变更 | `docs: {描述}` |
| 用户日常笔记 | 自由描述 |

提交粒度：Ingest 一次提交（知识文件 + LOG），Update 一次提交（知识文件 + LOG + L3 页面），Lint 一次提交（INDEX.md + 标记文件）。

推送流程：`git status → git add {文件} → git commit → git push`，push 失败则通知用户手动操作。

## 路径约定

- 所有路径使用正斜杠 `/`
- wikilink 推荐使用页面标题 `[[transformer]]`，不推荐使用路径
- 文件操作使用相对于 vault 根目录的路径
