---
title: "Parallelization（并行化）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - parallelization
  - workflow-pattern
  - sectioning
  - voting
  - concurrent-execution
  - consensus
status: published
summary: "Parallelization 是 Anthropic 定义的五种 workflow 模式之一，允许多个 LLM 同时处理任务并通过程序化方式聚合输出。包含两个关键变体：Sectioning（分段）将任务分解为独立子任务并行运行；Voting（投票）多次运行同一任务以获得多样化输出。适用于子任务可以并行以提速，或需要多视角/多次尝试以获得更高可信度结果的场景。对于有多个考量的复杂任务，当每个考量由单独的 LLM 调用处理时，LLM 通常表现更好。Sectioning 典型应用包括 guardrails 实现（一个模型处理查询，另一个筛查不当内容）；Voting 典型应用包括代码漏洞审查（多个 prompt 审查并标记问题）。"
---

## 定义

Parallelization 是允许多个 LLM 同时处理任务并通过程序化方式聚合输出的 workflow 模式，包含 Sectioning 和 Voting 两个变体。

![[parallelization-20260625170210.png]]

## 核心机制

### Sectioning（分段）

将任务分解为独立子任务并行运行，每个子任务关注不同方面。

### Voting（投票）

多次运行同一任务以获得多样化输出，通过投票或共识机制聚合结果。

## 适用场景

- 子任务可以并行以提速
- 需要多视角/多次尝试以获得更高可信度结果
- 复杂任务有多个独立考量，每个考量由单独 LLM 调用处理时效果更好

## 实用示例

### Sectioning 示例

- **Guardrails 实现**：一个模型实例处理用户查询，另一个筛查不当内容或请求，比同一 LLM 同时处理两者效果更好
- **自动化评估**：每个 LLM 调用评估模型表现的不同方面

### Voting 示例

- **代码漏洞审查**：多个不同 prompt 审查代码并标记问题
- **内容安全评估**：多个 prompt 评估内容是否不当，用不同投票阈值平衡误报和漏报

## 与其他模式的关系

- 与 [[prompt-chaining]] 的区别：Parallelization 是并行执行，Prompt Chaining 是顺序执行
- 与 [[orchestrator-workers]] 的区别：Parallelization 的子任务是预定义的，Orchestrator-Workers 的子任务是动态决定的
- 可与 [[routing]] 结合：先路由分类，再并行处理

## 相关概念

- [[augmented-llm]]
- [[agent-vs-workflow]]
