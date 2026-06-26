---
title: "Cohere"
layer: L3
kind: entity
entity_type: Organization
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
source: [3001-RAG与检索/contextual-retrieval.md]
tags: [cohere, reranking-provider, embedding-provider, nlp-platform, enterprise-ai, api-service, cohere-rerank]
status: draft
summary: "Cohere 是企业级 NLP API 提供商，专注于检索和生成技术。核心产品：Cohere Rerank API（重排序模型，$1/1M tokens）、Cohere Embed（嵌入模型）、Command 系列（生成模型）。在 Contextual Retrieval 实验中，Cohere Rerank 作为标准 reranking 工具，可将检索失败率从 2.9% 降至 1.9%。支持多语言，适合生产环境部署。除 reranking 外，还提供企业级 RAG 解决方案。"
---

# Cohere

## 简介

**Cohere** 是企业级 NLP API 提供商，专注于检索和生成技术。

## 核心产品

- **Cohere Rerank**：[[reranking]] API（$1/1M tokens）
- **Cohere Embed**：[[embedding]] API
- **Command 系列**：生成模型

## 在 Contextual Retrieval 中应用

实验使用 Cohere Rerank 作为标准 [[reranking]] 工具，性能提升显著：检索失败率 2.9% → 1.9%

## 特点

- 多语言支持
- 生产级稳定性
- 企业级 [[rag]] 解决方案

## 相关概念

- [[reranking]] — 核心产品
- [[contextual-retrieval]] — 应用场景
