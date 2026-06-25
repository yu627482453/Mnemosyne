---
title: "Agent（智能体）"
layer: L3
kind: topic
topic: "3000-Agent"
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - agent-architecture
  - workflow-patterns
  - tool-engineering
  - augmented-llm
  - agentic-systems
status: published
summary: "Agent 主题域涵盖基于大语言模型的智能体系统设计与实现。核心内容包括：Anthropic 提出的 Workflow 与 Agent 架构区分、Augmented LLM 作为基础构建块、五种 Workflow 编排模式（Prompt Chaining、Routing、Parallelization、Orchestrator-Workers、Evaluator-Optimizer）、自主 Agent 的决策循环机制、以及 Tool Engineering（ACI）工具设计方法论。该主题域关注从简单 LLM 调用到复杂自主 Agent 的完整复杂度谱系，强调从最简方案出发、仅在必要时增加复杂度的工程原则。"
---

## 主题域概述

Agent 主题域聚焦于基于大语言模型的智能体系统，涵盖从架构设计到工程实践的完整知识体系。

## 架构区分

- [[agent-vs-workflow]] — Workflow（预定义编排）与 Agent（动态决策）的架构区分
- [[augmented-llm]] — 增强型 LLM：检索 + 工具 + 记忆，所有 agentic 系统的原子构建块

## Workflow 模式

| 模式 | 控制方式 | 适用场景 |
|------|----------|----------|
| [[prompt-chaining]] | 顺序执行，前序输出驱动后续 | 可清晰分解的固定子任务 |
| [[routing]] | 分类分流，按类别选择路径 | 有明确类别的复杂任务 |
| [[parallelization]] | 并行执行（Sectioning / Voting） | 可并行加速或需多视角的任务 |
| [[orchestrator-workers]] | 中心 LLM 动态分解委派 | 子任务不可预测的复杂任务 |
| [[evaluator-optimizer]] | 生成-评估迭代循环 | 有明确评估标准的精修任务 |

## 工程实践

- [[tool-engineering]] — ACI（Agent-Computer Interface）设计方法论
- [[anthropic]] — Agent 领域核心研究机构
- [[swe-bench]] — 自主编码 Agent 基准测试

## 相关来源

- `3000-Agent/building-effective-agents.md` — 《构建高效的 AI Agent》（Anthropic）
