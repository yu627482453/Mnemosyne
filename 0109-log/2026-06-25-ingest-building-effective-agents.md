# 2026-06-25 Ingest 日志

## 来源
- 文件：`0003-inbox/Building Effective AI Agents.md`
- 标题：Building Effective AI Agents
- 来源：Anthropic 官方博客

## L2 创建
- 文件：`3000-Agent/building-effective-agents.md`
- ID：36636a47
- 主题：3000-Agent
- 状态：published
- 图片：8 张（全部下载成功）
- 标签：9 个（agent-architecture, workflow-patterns, prompt-chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, tool-engineering, augmented-llm）

## L3 创建

### Concepts（8 个）
1. `0102-wiki-concepts/agent/core/augmented-llm.md` — 增强型 LLM 基础构建块
2. `0102-wiki-concepts/agent/core/agent-vs-workflow.md` — Agent 与 Workflow 的架构区分
3. `0102-wiki-concepts/agent/core/tool-engineering.md` — ACI 工具设计方法论
4. `0102-wiki-concepts/agent/patterns/prompt-chaining.md` — 提示链 workflow 模式
5. `0102-wiki-concepts/agent/patterns/routing.md` — 路由 workflow 模式
6. `0102-wiki-concepts/agent/patterns/parallelization.md` — 并行化 workflow 模式
7. `0102-wiki-concepts/agent/patterns/orchestrator-workers.md` — 编排者-工人 workflow 模式
8. `0102-wiki-concepts/agent/patterns/evaluator-optimizer.md` — 评估者-优化者 workflow 模式

### Entities（2 个）
9. `0103-wiki-entities/organization/anthropic.md` — AI 安全公司，Claude 开发商
10. `0103-wiki-entities/project/swe-bench.md` — 自主编码 Agent 基准测试

## 配置更新
- `tag-vocabulary.yaml`：新增 48 个标签
- `topics.yaml`：AI技术 domain active 追加 3000-Agent
- `.wiki.db`：全量重建索引（28 notes）
- L2 `planned_links`：清理 8 个已创建概念，保留 1 个未创建（model-context-protocol）

## 修复
- `agent-vs-workflow` 从 `0102-wiki-concepts/agent/core/` 迁移到 `0104-wiki-comparisons/system-architecture/`，kind 改为 comparison，补充 comparison_axis/lhs/rhs 字段
- CLAUDE.md 步骤 8 细化为 8a-8f 六项检查清单

## 校验结果
- Frontmatter 校验：11/11 通过
- Summary 长度：全部满足 ≥200 字符要求
- 图片下载：8/8 成功
