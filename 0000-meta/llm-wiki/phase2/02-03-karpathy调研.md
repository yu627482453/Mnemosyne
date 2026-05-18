# 2.3 karpathy-llm-wiki 调研

> 日期：2026-05-14 | 项目：[Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)（714⭐）

## 一、项目概述

Andrej Karpathy 提出的 LLM Wiki 理念——"LLM 负责编写和维护 wiki，人类负责阅读和提问"。`Astro-Han/karpathy-llm-wiki` 是其最成熟的社区实现，以 Agent Skills 格式封装为可安装的技能包。

核心理念：**"编译模式"替代传统 RAG**——摄入时就将原始素材编译为结构化 wiki 页面，知识随时间复利增长，而非每次查询时从零检索。

## 二、架构分析

### 目录结构

```
project/
├── raw/                  # 不可变原始素材
│   └── topic/
│       └── 2026-04-03-slug.md
├── wiki/                 # LLM 维护的知识页面
│   ├── topic/
│   │   └── concept.md
│   ├── index.md          # 全局索引
│   └── log.md            # 追加式操作日志
└── SKILL.md              # 规则层（Schema + 工作流）
```

### 三操作模型

| 操作 | 触发 | 行为 |
|------|------|------|
| **Ingest** | 用户提供 URL/文件/文本 | Fetch → raw/ → Compile → wiki/ → Cascade Update → 更新 index + log |
| **Query** | 用户提问 | 查 index → 读 wiki → 合成回答（引用链接） |
| **Lint** | 用户要求检查 | 索引一致性/死链/raw 引用/See Also，部分自动修复 |

### 关键设计细节

**Ingest 流程**：
1. 获取源内容，存入 `raw/<topic>/YYYY-MM-DD-slug.md`（不可变）
2. 编译到 wiki/：同主题合并、新概念新建、跨主题加 See Also
3. **级联更新**：检查同主题和相关主题，更新所有受影响页面
4. 事实冲突时标注来源分歧
5. 更新 index.md + 追加 log.md

**Lint 系统**：
- 自动修复：索引一致性、内部死链、raw 引用路径、See Also
- 报告不修：事实矛盾、过时内容、孤立页面、缺失跨主题引用、应存在的缺失概念

**文章元数据格式**：
```yaml
---
title: "概念名称"
tags: [tag1, tag2]
Sources: "作者/来源, 2024-01-15; 另一来源, 2024-03"
Raw: "../../raw/topic/file.md"
Updated: "2026-04-03"
---
```

## 三、与我们设计的对比

| 维度 | karpathy-llm-wiki | 我们的设计 |
|------|-------------------|-----------|
| **数据层** | `raw/` → `wiki/`（2 层） | `inbox/` → 主题目录 → `0100-0104/`（3 层） |
| **ID 体系** | 无显式 ID，靠文件路径 | `{目录编号}-{序号}` 唯一 ID |
| **知识分类** | 按主题目录（wiki/ 下仅一层） | 按类型分区（概念/实体/主题/比较） |
| **LLM 角色** | LLM 全权维护 wiki | Claude 手动触发，协助加工 |
| **前端** | 纯 Markdown | Obsidian + 插件生态 |
| **元数据** | Sources / Raw / Updated | 完整 Frontmatter（id/type/domain/tags/links/summary） |
| **变更追踪** | log.md 追加 | Git commit + 0109-log/ |
| **质量保障** | Lint 系统 | Claude Code 手动审查 |

## 四、可借鉴的设计

### 4.1 立即采用

| 设计 | 说明 | 落地位置 |
|------|------|----------|
| **操作日志** | `log.md` 追加式记录每次 ingest/query/lint 操作 | `0109-log/LOG-YYYY-MM-DD.md` |
| **级联更新** | 新知识入库后检查并更新受影响的相关页面 | Claude 工作流（P1） |
| **冲突标注** | 不同来源存在矛盾时显式标注 | 知识模板中增加 "争议" 区块 |
| **不可变原始素材** | inbox 中原始素材标记为不可变，只加工不修改 | `0003-inbox/` 规范 |

### 4.2 适配后采用

| 设计 | 原因 | 适配方案 |
|------|------|----------|
| **Lint 系统** | 自动修复 + 报告模式很好 | 单独设计为 Claude 检查规则集，而非实时自动执行 |
| **Archive 页面** | Query 结果存为 wiki 页面 | 归入 `0004-outbox/` 而非混入知识库 |
| **单层主题目录** | 不适合我们的 4 知识域 | 保留我们的多层结构，Lint 逻辑适配 |

### 4.3 不适用

| 设计 | 原因 |
|------|------|
| LLM 全权维护 wiki | 用户偏好手动触发，逐步自动化 |
| SKILL.md 单文件封装 | 我们的系统更复杂，需多文件组织 |
| raw/ 按主题分目录 | 我们的 inbox 是暂存区，按时间而非主题 |

## 五、2.3 结论

karpathy-llm-wiki 的核心价值在于**工作流设计**而非目录结构。最有价值的借鉴点：

1. **级联更新机制**：新知识入库→检查关联页面→更新受影响内容。这是我们 P1 阶段 Claude 工作流的核心参考
2. **操作日志（log.md）**：简单但强大的审计追踪，适合知识库这种长期演进系统
3. **Lint 检查清单**：索引一致性、死链接、跨主题引用缺失——可作为 Claude 定期检查规则
4. **"编译模式"思维**：我们的三层架构本质上就是编译模式——inbox（源码）→ 基础层（编译）→ 关系层（链接）

**关键判断**：我们的三层架构比 karpathy-llm-wiki 的两层更强，但工作流设计（Ingest/Lint/Cascade）值得直接借鉴。

---

