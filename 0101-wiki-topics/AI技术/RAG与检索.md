---
title: "RAG与检索"
layer: L3
kind: topic
topic: "3001-RAG与检索"
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
tags: [rag, retrieval, embedding, semantic-search, knowledge-base, llm-application]
status: draft
summary: "检索增强生成（RAG）技术域，涵盖语义检索、精确匹配、上下文增强、重排序等核心技术。RAG 通过从外部知识库动态检索相关信息来增强 LLM 响应质量，是构建企业级 AI 应用的关键技术。本主题包含 RAG 基础架构、检索优化方法、主流工具和实践案例。"
---

# RAG与检索

## 概述

检索增强生成（RAG）是 LLM 应用的核心技术，通过外部知识库检索增强模型响应能力。

## 核心概念

### 基础架构
- [[rag]] — RAG 系统基础
- [[embedding]] — 向量嵌入与语义检索
- [[bm25]] — 词汇精确匹配

### 优化技术
- [[contextual-retrieval]] — 上下文检索（Anthropic，检索失败率↓49%）
- [[reranking]] — 二次重排序优化

### 相关技术
- [[prompt-caching]] — 提示词缓存（成本优化）

## 主要产品与工具

- [[voyage-ai]] — Voyage Embeddings & Reranker
- [[cohere]] — Cohere Rerank API

## 来源文档

### L2 标准化数据
- [[contextual-retrieval|Contextual Retrieval：上下文检索技术]] (3001-RAG与检索/)
