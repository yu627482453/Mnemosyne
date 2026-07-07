---
title: "Prompt Chaining（提示链）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - prompt-chaining
  - workflow-pattern
  - sequential-processing
  - quality-gate
  - task-decomposition
status: published
summary: "Prompt Chaining 是 Anthropic 定义的五种 workflow 模式之一，将任务分解为一系列顺序步骤，每个 LLM 调用处理前一步的输出。可以在任何中间步骤添加程序化检查（gate），确保流程仍在正轨上。适用于任务可以清晰分解为固定子任务的情况，主要目标是用延迟换取更高准确度，使每次 LLM 调用处理更简单的任务。典型应用场景包括：先生成营销文案然后翻译成另一种语言；先写文档大纲、检查是否满足标准、然后基于大纲撰写文档。Prompt Chaining 是最简单直观的 workflow 模式，适合作为 agentic 系统设计的起点。"
---

## 定义

Prompt Chaining 是将任务分解为一系列顺序步骤的 workflow 模式，每个 LLM 调用处理前一步的输出，可在中间步骤插入程序化检查（gate）。

![[0001-resource/3000-Agent/building-effective-agents-prompt-chaining-20260625230615.png]]

## 核心机制

- **顺序执行**：前一步的输出作为后一步的输入
- **质量关卡**：可在任意中间步骤添加 gate 检查，确保流程在正轨
- **任务简化**：每次 LLM 调用只处理一个简单子任务

## 适用场景

适用于任务可以清晰分解为固定子任务的情况，主要目标是用延迟换取更高准确度。

## 实用示例

- **多语言内容生成**：先生成营销文案，然后翻译成另一种语言
- **结构化文档撰写**：先写文档大纲 → 检查大纲是否满足特定标准 → 基于大纲撰写完整文档

## 与其他模式的关系

- 与 [[routing]] 的区别：Prompt Chaining 是顺序处理，Routing 是分类分流
- 与 [[parallelization]] 的区别：Prompt Chaining 是串行，Parallelization 是并行
- 与 [[orchestrator-workers]] 的区别：Prompt Chaining 的子任务是预定义的，Orchestrator-Workers 的子任务是动态决定的

## 相关概念

- [[augmented-llm]]
- [[agent-vs-workflow]]
