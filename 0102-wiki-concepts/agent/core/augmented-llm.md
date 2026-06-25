---
title: "Augmented LLM（增强型大语言模型）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - augmented-llm
  - llm-architecture
  - retrieval
  - tool-use
  - memory
  - model-context-protocol
status: published
summary: "Augmented LLM 是 Agentic 系统的基础构建块，指通过增强能力（检索、工具调用、记忆）提升的大语言模型。与基础 LLM 不同，Augmented LLM 能主动生成搜索查询、选择合适的工具、决定保留什么信息。Anthropic 建议关注两个关键实现方面：将增强能力针对特定用例进行定制，以及确保为 LLM 提供简单、文档完善的接口。Model Context Protocol（MCP）是实现这些增强的一种方法，允许开发者通过简单的客户端实现与第三方工具生态集成。Augmented LLM 是所有 workflow 模式和自主 agent 的原子单元，理解其能力边界是设计复杂 agentic 系统的前提。"
---

## 定义

Augmented LLM 是通过检索（retrieval）、工具调用（tools）和记忆（memory）三种增强能力提升的大语言模型，是 Anthropic 定义的 Agentic 系统的基础构建块。

## 核心特征

- **主动检索**：模型能自主生成搜索查询，而非被动等待用户提供上下文
- **工具选择**：模型根据任务需求选择合适的工具，而非硬编码调用链
- **记忆管理**：模型决定保留什么信息，支持跨会话的状态维护
- **接口设计**：增强能力需要为 LLM 提供简单、文档完善的接口

## 实现建议

Anthropic 建议关注两个方面：
1. 将增强能力针对特定用例进行定制
2. 确保为 LLM 提供简单、文档完善的接口

Model Context Protocol（MCP）是实现这些增强的一种标准化方法，允许开发者通过简单的客户端实现与不断增长的第三方工具生态集成。

## 在 Agentic 系统中的角色

Augmented LLM 是所有 workflow 模式（prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer）和自主 agent 的原子单元。无论系统复杂度如何，每个 LLM 调用都应具备这些增强能力。

## 相关概念

- [[agent-vs-workflow]]
- [[tool-engineering]]
