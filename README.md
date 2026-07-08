# Mnemosyne — LLM Wiki System

基于 Obsidian + Claude Code 的智能本地 Wiki 系统，将原始素材编译为结构化知识库。

## 架构

三层设计（L1 → L2 → L3）：

| 层级 | 定位 | 目录 |
|------|------|------|
| L1 原始数据层 | 未加工素材 | `0003-inbox/` |
| L2 主题知识层 | 高保真标准化数据（source of truth） | `{编号}-{主题名}/` |
| L3 知识加工层 | concept / entity / comparison 派生 page | `0101-0104/` |

写入 L1→L2→L3，查询 L3→L2→L1。

## 快速开始

1. 将素材放入 `0003-inbox/`
2. 在 Claude Code 中 `@` 引用该文件
3. Claude 自动执行 Ingest：判断主题域 → 生成 slug → 创建 L2 → 派生 L3 → 验收 → git commit

```bash
cd vault && claude
```

CLAUDE.md 自动加载所有规则。

## 目录

```
{编号}-{主题名}/          # L2（按需）
0000-meta/0001-templates/ # 知识模板
0100-wiki-meta/
├── configs/              # schema + topics + tags + lint
└── scripts/              # skill 工作流 + 校验脚本
0003-inbox/               # L1 原始
0101-wiki-topics/         # L3 主题综述
0102-wiki-concepts/       # L3 概念
0103-wiki-entities/       # L3 实体（按类型）
0104-wiki-comparisons/    # L3 对比（按轴）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
```

## 核心功能

- **Ingest**：L1 inbox → 图片本地化 → 高保真 L2（含原文主体翻译）→ L3 typed wiki
- **Query**：SQLite FTS5全文检索 + 多因子排序（文本50%+入链25%+新鲜度15%+质量10%），GraphRAG路径查询
- **Update**：三级变更（轻微/中等/重大），自动级联 L3
- **Lint**：16项自动检查（断链/hash/命名/资源一致性等）
- **校验**：写入前强制10项schema校验

## 规范

- Frontmatter 严格类型化（L2: id/hash/tags≥5/summary 200-500；L3: processing_path/entity_type/comparison_axis）
- 文件命名：空格→`-`，`.`→`_`，title 保留原文
- wikilink 优先标题格式 `[[slug]]`
- 图片路径：`0001-resource/{topic}/{slug}/{timestamp}.{ext}`
- 模型分层：翻译/Lint/检索用 Haiku；写作/判断用 Opus

## Hooks

- **PostToolUse**（Write/Edit）：自动校验 frontmatter 符合 schema
- **Stop**：退出时提醒 git status
- **Cron**：每日 7:07 Lint 检查 + 18:17 git push

## 决策记录

见 `0100-wiki-meta/DECISIONS.md`（D001-D019）。

## 技术栈

- **存储**：Obsidian Markdown + SQLite (FTS5全文索引)
- **检索**：BFS路径查找 + 多因子排序算法
- **缓存**：hot.md查询历史 + LRU内存缓存
- **自动化**：Claude Code + Python脚本

## 当前规模

- 总文件：19个 (L3: 12个)
- 总链接：139个
- 标签词表：127个
- 主题域：1个 (Agent)
