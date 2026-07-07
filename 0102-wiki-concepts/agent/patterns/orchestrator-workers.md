---
title: "Orchestrator-Workers（编排者-工人）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - orchestrator-workers
  - workflow-pattern
  - dynamic-decomposition
  - task-delegation
  - result-synthesis
status: published
summary: "Orchestrator-Workers 是 Anthropic 定义的五种 workflow 模式之一，由中心 LLM（orchestrator）动态分解任务，委派给 worker LLM，并综合它们的结果。与 Parallelization 的关键区别在于灵活性：子任务不是预定义的，而是由 orchestrator 根据具体输入动态决定。适用于无法预测所需子任务的复杂任务，例如编码中需要更改的文件数量和每个文件中的变更性质都取决于具体任务。典型应用包括每次对多个文件进行复杂更改的编码产品，以及涉及从多个来源收集和分析可能相关信息的搜索任务。Orchestrator-Workers 是 workflow 模式中最接近自主 agent 的模式。"
---

## 定义

Orchestrator-Workers 是由中心 LLM（orchestrator）动态分解任务、委派给 worker LLM、并综合结果的 workflow 模式。

![[0001-resource/3000-Agent/building-effective-agents-orchestrator-workers-20260625230615.png]]

## 核心机制

- **动态分解**：orchestrator 根据具体输入决定需要哪些子任务
- **任务委派**：将子任务分配给专门的 worker LLM
- **结果综合**：orchestrator 聚合各 worker 的输出，形成最终结果

## 与 Parallelization 的区别

两者拓扑相似，但关键区别在于灵活性：
- **Parallelization**：子任务是预定义的（sectioning 或 voting）
- **Orchestrator-Workers**：子任务由 orchestrator 动态决定

## 适用场景

适用于无法预测所需子任务的复杂任务，子任务数量和性质取决于具体输入。

## 实用示例

- **复杂编码任务**：每次对多个文件进行复杂更改，需要更改的文件数量和变更性质都取决于具体任务
- **多源信息搜索**：涉及从多个来源收集和分析可能相关信息，orchestrator 决定搜索哪些来源、如何综合结果

## 与其他模式的关系

- 与 [[parallelization]] 的区别：子任务是动态决定而非预定义
- 与 [[agent-vs-workflow]] 的关系：是 workflow 模式中最接近自主 agent 的模式
- 可结合 [[routing]]：orchestrator 根据任务类型选择不同的 worker 策略

## 相关概念

- [[augmented-llm]]
- [[tool-engineering]]
