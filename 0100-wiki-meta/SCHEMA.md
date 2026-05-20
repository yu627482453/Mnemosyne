# 知识 Schema

> 面向人阅读的 Schema 说明。机器校验规则见 `0000-meta/0003-configs/schema.yaml`。

## Frontmatter 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 知识标题 |
| `topic` | string | ✅ L2 | 所属主题目录名 |
| `layer` | enum | ✅ | L1 / L2 / L3 |
| `kind` | enum | ✅ | L2 固定为 standard；L3 为 topic/concept/entity/comparison |
| `tags` | list | | 3-10 个关键词（推荐 8+），遵循 `tag-vocabulary.yaml` |
| `aliases` | list | | 含 slug 的别名列表 |
| `created` | date | ✅ L2 | YYYY-MM-DD，L2 必填；L3 以 updated 代创建时间 |
| `updated` | date | ✅ | YYYY-MM-DD，每次修改时更新 |
| `source` | enum | | manual / url / file / claude |
| `status` | enum | ✅ | L1: raw/processing/archived；L2/L3: draft/published |
| `summary` | string | ✅ | 一句话摘要，≤80字 |
| `processing_path` | string | L3 | 加工路径：`{大类}/{主题域}` |
| `entry_count` | number | L3 | 当前页引用的 L2 条目数量 |
| `source_topics` | list | L3 | 覆盖的 L2 主题目录列表 |
| `source_url` | string | L1 | 原始 URL（仅 inbox） |
| `date` | date | L1 | 采集日期（仅 inbox） |

## status 流转

**L1 inbox**：`raw` → `processing` → 归档/删除
**L2/L3**：`draft` → `published`
