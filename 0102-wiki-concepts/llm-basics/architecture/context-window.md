---
title: "上下文窗口（Context Window）"
layer: L3
kind: concept
processing_path: "AI技术/LLM基础"
updated: 2026-07-07
source: ["待补充"]
tags: [context-window, token-limit, llm-constraint, prompt-engineering, input-length]
status: draft
summary: "上下文窗口是LLM单次处理的最大token数量限制，包含输入提示词和输出生成内容。不同模型的窗口大小不同，从早期的2K到现代的100K+甚至200K。窗口大小直接影响模型能够理解的信息量和任务复杂度，是设计RAG系统和Agent时的关键约束。"
---

## 定义

Context Window是LLM单次处理的最大token数量，是模型架构的核心约束。

## 核心机制

- Token计数限制
- 输入输出总和限制
- 窗口大小影响任务设计

## 相关概念

- [[prompt-caching]]
- [[rag]]
