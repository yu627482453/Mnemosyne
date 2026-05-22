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
| `0100-wiki-meta/scripts/skill-ingest.md` | 摄入流程 |
| `0100-wiki-meta/scripts/skill-lint.md` | 检查流程 |

## Frontmatter（摘要）

