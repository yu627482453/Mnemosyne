---
title: "Augmented LLM"
layer: L3
kind: concept
processing_path: AI技术/Agent
updated: 2026-06-25
source: [3000-Agent/building-effective-agents.md]
tags: [augmented-llm, llm-enhancement, retrieval, tool-use, agent-basics]
status: published
summary: 最简单的 Agent 模式，通过检索和工具调用增强 LLM 能力。单次调用完成任务，最小延迟和成本，适用于直接任务场景。生产环境最常见的 Agent 实现。
---

## 定义

Augmented LLM 通过检索增强（RAG）和工具调用扩展 LLM 功能。

## 核心特点

- 单次调用完成
- 最小延迟和成本
- 简单可控

## 使用场景

✅ 客服聊天、文档问答、简单自动化
❌ 多步推理、条件分支、自主规划

## 关系

基础层，是 [[prompt-chaining]] 和 [[agent-loop]] 的起点。

源自：[[building-effective-agents]]
