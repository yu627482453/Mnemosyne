---
title: "RAG：检索增强生成"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
source: [3001-RAG与检索/contextual-retrieval.md]
tags: [rag, retrieval, knowledge-base, prompt-augmentation, vector-search, llm-application, context-injection, information-retrieval]
status: draft
summary: "RAG（Retrieval-Augmented Generation）通过从外部知识库检索相关信息并注入提示词来增强 LLM 响应。核心流程：文档分块 → 向量化存储 → 语义检索 → 上下文注入。解决 LLM 知识固化、幻觉和领域知识缺失问题。现代 RAG 结合 embedding 和 BM25，使用 reranking 提升准确性。小知识库（< 200k tokens）可直接用 prompt caching 放入上下文窗口，无需 RAG。"
---

# RAG：检索增强生成

## 定义

**RAG（Retrieval-Augmented Generation）** 将信息检索与 LLM 结合，通过动态检索相关背景知识来增强模型输出质量。

## 工作原理

**预处理**：文档切块 → [[embedding]] → [[vector-database]]  
**运行时**：查询编码 → 相似度检索 → 上下文注入 → LLM 生成

## 技术演进

- **传统 RAG**：语义检索
- **混合 RAG**：语义 + [[bm25]]
- **上下文增强**：[[contextual-retrieval]]（失败率 ↓49%）

## 适用场景

| 知识库大小 | 方案 |
|-----------|------|
| < 200k tokens | 直接用 [[prompt-caching]] |
| > 200k tokens | 使用 RAG |

## 相关概念

- [[embedding]] — 向量化
- [[bm25]] — 精确匹配
- [[reranking]] — 二次排序
- [[contextual-retrieval]] — 优化方法
