---
title: "Routing（路由）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - routing
  - workflow-pattern
  - classification
  - task-dispatch
  - model-selection
status: published
summary: "Routing 是 Anthropic 定义的五种 workflow 模式之一，对输入进行分类并将其导向专门的后续任务。这种模式允许关注点分离，构建更专业化的 prompt。没有 Routing，针对一种输入类型的优化可能损害其他输入的表现。适用于有明确类别、各类别需分别处理的复杂任务，且分类能被 LLM 或传统分类模型/算法准确处理。典型应用包括：将不同类型的客服查询（一般问题、退款请求、技术支持）导向不同的下游流程和工具；将简单问题路由到成本高效的模型（如 Claude Haiku），将复杂问题路由到更强大的模型（如 Claude Sonnet）以优化性能成本比。"
---

## 定义

Routing 是对输入进行分类并将其导向专门后续任务的 workflow 模式，实现关注点分离和专业化 prompt 构建。

![[routing-20260625170210.png]]

## 核心机制

- **输入分类**：通过 LLM 或传统分类模型识别输入类别
- **专门处理**：不同类别导向不同的下游流程、prompt 和工具
- **关注点分离**：避免针对一种输入的优化损害其他输入的表现

## 适用场景

适用于有明确类别、各类别需分别处理的复杂任务，且分类能被准确处理。

## 实用示例

- **客服查询分流**：将一般问题、退款请求、技术支持导向不同的下游流程和工具
- **模型选择优化**：将简单/常见问题路由到成本高效的模型（如 Claude Haiku 4.5），将困难/罕见问题路由到更强大的模型（如 Claude Sonnet 4.5）

## 与其他模式的关系

- 与 [[prompt-chaining]] 的区别：Routing 是分类分流，Prompt Chaining 是顺序处理
- 与 [[parallelization]] 的区别：Routing 按类别选择路径，Parallelization 按任务拆分并行
- Routing 常作为其他模式的前置步骤

## 相关概念

- [[augmented-llm]]
- [[agent-vs-workflow]]
