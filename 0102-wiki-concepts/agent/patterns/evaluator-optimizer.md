---
title: "Evaluator-Optimizer（评估者-优化者）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - evaluator-optimizer
  - workflow-pattern
  - iterative-refinement
  - feedback-loop
  - quality-assessment
status: published
summary: "Evaluator-Optimizer 是 Anthropic 定义的五种 workflow 模式之一，一个 LLM 调用生成响应，另一个提供评估和反馈，形成循环迭代。适用于有明确评估标准且迭代改进能提供可衡量价值的场景。两个良好适配的标志：第一，当人类明确表达反馈时 LLM 响应能明显改进；第二，LLM 能提供这样的反馈。这类似于人类作家撰写精修文档时经历的迭代写作过程。典型应用包括文学翻译（翻译 LLM 初次可能无法捕捉细微差别，评估 LLM 提供有用批评）和复杂搜索任务（需要多轮搜索和分析，评估者决定是否需要进一步搜索）。"
---

## 定义

Evaluator-Optimizer 是一个 LLM 生成响应、另一个提供评估和反馈、形成循环迭代的 workflow 模式。

![[0001-resource/3000-Agent/building-effective-agents-evaluator-optimizer-20260625230615.png]]

## 核心机制

- **生成-评估循环**：一个 LLM 生成响应，另一个评估并提供反馈
- **迭代改进**：基于反馈不断优化输出质量
- **终止条件**：达到评估标准或最大迭代次数

## 适用场景判断

两个良好适配的标志：
1. 当人类明确表达反馈时，LLM 响应能明显改进
2. LLM 能提供有效的评估反馈

## 适用场景

适用于有明确评估标准且迭代改进能提供可衡量价值的场景。

## 实用示例

- **文学翻译**：翻译 LLM 可能初次无法捕捉细微差别，但评估 LLM 能提供有用的批评，通过多轮迭代提升翻译质量
- **复杂搜索任务**：需要多轮搜索和分析来收集全面信息，评估者决定是否需要进一步搜索

## 与其他模式的关系

- 与 [[prompt-chaining]] 的区别：Evaluator-Optimizer 是循环迭代，Prompt Chaining 是单向顺序
- 与 [[parallelization]] 的 Voting 变体区别：Voting 是多次运行取共识，Evaluator-Optimizer 是基于反馈迭代改进
- 可结合 [[routing]]：根据评估结果路由到不同的优化策略

## 相关概念

- [[augmented-llm]]
- [[agent-vs-workflow]]
