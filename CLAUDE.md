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
| `0000-meta/llm-wiki/CURRENT.md` | 方案入口 |
| `0000-meta/llm-wiki/DECISIONS.md` | 决策记录 |
| `0000-meta/0003-configs/schema.yaml` | 字段校验 |
| `0000-meta/0003-configs/topics.yaml` | 主题映射 |
| `0000-meta/0003-configs/tag-vocabulary.yaml` | 受控标签词表 |
| `0000-meta/0003-configs/lint-rules.yaml` | 健康检查 |

## Frontmatter（摘要）

**L2** — title, topic, layer:L2, kind:standard, tags(5-10, 无空格, 多词连字符), aliases, created, updated, source, source_url, resource_refs, status(draft/published), summary(200-500字)

**L3 concept** — title, layer:L3, kind:concept, processing_path, updated, source([L2路径]), tags, summary(200-500字)

**L3 entity** — title, layer:L3, kind:entity, entity_type(Organization/Product/Project/Paper/Person), updated, source, tags, summary

**L3 comparison** — title, layer:L3, kind:comparison, comparison_axis, lhs, rhs, updated, source, tags, summary

**L1** — title, date, source, source_url, status(raw/processing/archived)

> 完整校验见 schema.yaml。

## 目录结构

```
{编号}-{主题名}/          # L2（按需创建）
0000-meta/                # 模板/脚本/配置
0003-inbox/               # L1（含 .trash/）
0101-wiki-topics/         # L3 主题综述（域级：大类/主题域.md）
0102-wiki-concepts/       # L3 概念（按主题域：大类/主题域/{slug}.md）
0103-wiki-entities/       # L3 实体（按类别：{entity_type}/{slug}.md）
0104-wiki-comparisons/    # L3 对比（按比较轴：{comparison_axis}/{slug}.md）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
```

## 四操作规范

### Ingest（L1 → L2 → L3）

1. 用户 @ 引用 inbox 文件 → 读取
2. 判断归属主题目录（首次归档到某域须用户确认）
3. 生成 slug（英文优先，3-5 推荐，rg --files 查重）
4. 按 t-knowledge.md 创建 L2（高保真，不过度摘要；默认中文；tags 5-10 无空格连字符；summary 200-500 字）
5. L3 触发：concept 按主题域归档，entity 按 entity_type 归档，comparison 按 comparison_axis 归档
6. 死链治理：正式链接仅指已存在页面，未建概念入 planned_links
7. 跨主题引用建议
8. LOG + .trash/ + git commit

### Query（L3 topic 优先 → L2 → L1）

1. rg 0101 找匹配主题域 → 域内 rg 0102-0104
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

自动修复：断裂 wikilink
报告：孤立页面、draft>30天、Frontmatter 不完整、summary 超范围、tags 格式、L3 source 失效、L3 独立事实

## 落盘验收清单

1. frontmatter 字段齐全
2. tags 5-10 个、无空格、多词连字符
3. summary 200-500 字
4. 链接正确
5. L3 source 明确
6. resource_refs 与正文 `![[...]]` 对应
7. 死链已处理

## Git

| 场景 | 格式 |
|------|------|
| 知识操作 | `wiki: {操作} {文件} — {摘要}` |
| 文档变更 | `docs: {描述}` |

流程：用户确认后 `git status → add → commit → push`
