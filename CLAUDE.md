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
| `0100-wiki-meta/configs/schema.yaml` | 字段校验 |
| `0100-wiki-meta/configs/topics.yaml` | 主题映射 |
| `0100-wiki-meta/configs/tag-vocabulary.yaml` | 受控标签词表 |
| `0100-wiki-meta/configs/lint-rules.yaml` | 健康检查 |

## Frontmatter（摘要）

**L2** — id, title, topic, layer:L2, kind:standard, tags(5-10, 无空格, 多词连字符), aliases, created, updated, source, source_url, resource_refs, content_hash, status(draft/published), summary(200-500字)

**L3 concept** — title, layer:L3, kind:concept, processing_path, updated, source([L2路径]), tags, summary(200-500字)

**L3 entity** — title, layer:L3, kind:entity, entity_type(Organization/Product/Project/Paper/Person), updated, source, tags, summary

**L3 comparison** — title, layer:L3, kind:comparison, comparison_axis, lhs, rhs, updated, source, tags, summary

**L1** — title, date, source, source_url, status(raw/processing/archived)

> 完整校验见 schema.yaml。

## 命名规则

- 文件名禁止空格 → 空格统一转 `-`
- 文件名主体中的 `.` → 转 `_`（仅最后一个 `.` 是扩展名）
- slug 仅用于路径定位，不替代标题；L2 title 保留原始标题
- 图片资源：`0001-resource/{topic}/{slug}/{timeStamp}.{ext}`

## 目录结构

```
{编号}-{主题名}/          # L2（按需创建）
0000-meta/                # 模板/脚本/配置
0001-resource/            # 本地资源（图片/附件）
0003-inbox/               # L1
0101-wiki-topics/         # L3 主题综述（域级）
0102-wiki-concepts/       # L3 概念（按主题域）
0103-wiki-entities/       # L3 实体（按 entity_type）
0104-wiki-comparisons/    # L3 对比（按 comparison_axis）
0105-wiki-base/           # Base 面板
0109-log/                 # 操作日志
.trash/                   # 回收站
```

## 四操作规范

### Ingest（L1 → L2 → L3）

1. 用户 @ 引用 inbox → 读取 → 扫描图片
2. 判断归属主题目录（首次归档须用户确认）
3. 生成 slug（英文优先，3-5 推荐）；文件名按命名规则处理
4. 图片落地：下载 → `0001-resource/{topic}/{slug}/{timeStamp}.{ext}` → 改写正文 → 写入 resource_refs
5. 创建 L2：标题保留原文；必须包含 核心内容 + 文章要点 + **原文主体（中文翻译，保留段落层次）** + 来源
6. L3 触发：concept/entity/comparison **主动逐项检查**（不因主轴是 concept 就跳过 entity）
7. 死链治理 + 跨主题引用
8. LOG + .trash/ + git commit

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

自动修复：断裂 wikilink
报告：L2 缺原文主体、孤立页面、draft>30天、Frontmatter 不完整、summary 超范围、tags 格式、文件名格式、resource_refs 不一致、远程图片残留、L3 source 失效、L3 独立事实

## 落盘验收清单

1. frontmatter 字段齐全
2. L2 包含原文主体区块
3. tags 5-10、无空格、连字符
4. summary 200-500 字
5. 图片已落地、resource_refs 1:1、无远程图片残留
6. entity/comparison 已主动检查
7. 文件名符合命名规则
8. 死链已处理

## Git

| 场景 | 格式 |
|------|------|
| 知识操作 | `wiki: {操作} {文件} — {摘要}` |
| 文档变更 | `docs: {描述}` |

流程：用户确认后 `git status → add → commit → push`

## 设计决策

### 架构
- **D001**: L1原始→L2高保真标准化→L3 typed wiki。写入L1→L2→L3，查询L3→L2→L1。
- **D003**: L2统一kind:standard，不区分concept/entity/comparison。
- **D004**: topic/concept/entity/comparison属L3加工形态。
- **D013**: L3按概念/实体/对比独立建页；0101为域级主题综述。
- **D015**: entity按entity_type归档；comparison按comparison_axis归档；concept按主题域。
- **D016**: L2必须含原文主体，不允许过度摘要化。

### 字段
- **D006**: L3使用processing_path。
- **D012**: source保持单一字段。
- **D014**: L3 source为文件级L2路径列表。
- **D019**: L2 id=SHA256(topic+slug+created)[:8]；content_hash=SHA256(全文)[:8]。

### 操作
- **D008**: L1标准化后移入.trash/，用户确认后执行。
- **D009**: slug英文优先，3-5推荐选项。
- **D010**: L3不允许人工编辑内容逻辑。
- **D011**: tags词表收敛到tag-vocabulary.yaml。
- **D017**: 正式wikilink仅链接已存在页面；未建概念入planned_links。
- **D018**: 文件名空格→-，主体.→_；title保留原始标题。

## 待验证
- 正式Ingest（entity/comparison主动触发效果）
- 图片下载→本地→引用全链路
- 多来源级联合并 / Lint完整流程 / 跨主题引用效果
