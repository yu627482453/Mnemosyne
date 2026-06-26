---
title: "Contextual Retrieval：上下文检索"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
source:
  - 3001-RAG与检索/contextual-retrieval.md
tags: [contextual-retrieval, rag-optimization, contextual-embeddings, contextual-bm25, chunk-contextualization, retrieval-accuracy, anthropic-technique, prompt-caching]
status: draft
summary: "Contextual Retrieval 是 Anthropic 提出的 RAG 检索优化方法，核心是在文档分块后、embedding 和建立 BM25 索引之前，使用 LLM 为每个 chunk 生成简洁的上下文说明（50-100 tokens），解决传统 RAG 因切块导致的上下文丢失问题。技术包括 Contextual Embeddings 和 Contextual BM25 两部分。实验表明：单独使用 Contextual Embeddings 可将检索失败率降低 35%（5.7%→3.7%），结合 Contextual BM25 降低 49%（5.7%→2.9%），再加上 reranking 可降低 67%（5.7%→1.9%）。配合 prompt caching 技术，为每百万文档 tokens 生成上下文的成本仅 $1.02。方法对现有 RAG 系统侵入性小，仅需改造预处理阶段，无需修改检索架构。"
---

# Contextual Retrieval：上下文检索

## 定义

**Contextual Retrieval** 是一种 [[rag]] 检索增强技术，通过在文档分块后为每个 chunk 添加情境化的上下文说明，然后再进行 [[embedding]] 和 [[bm25]] 索引，从而提升检索准确率。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-2.png]]

## 核心问题

传统 RAG 在文档切块时会破坏上下文完整性。例如某个 chunk 写着"公司营收增长 3%"，但不知道是哪家公司、哪个季度。

## 技术方案

### Contextual Embeddings
为每个 chunk 添加上下文后再 embedding，检索失败率 ↓35%（5.7% → 3.7%）

### Contextual BM25
为每个 chunk 添加上下文后再建立 BM25 索引

### 组合效果
- Contextual Embeddings + BM25：↓49%（5.7% → 2.9%）
- + Reranking：↓67%（5.7% → 1.9%）

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-3.png]]

## 实施方法

使用 Claude 为每个 chunk 生成上下文（50-100 tokens）：

```xml
<document>{{WHOLE_DOCUMENT}}</document> 
<chunk>{{CHUNK_CONTENT}}</chunk> 
请给出简短上下文，以便将这个块定位在整个文档中。
```

**成本优化**：使用 [[prompt-caching]] 降低成本至 $1.02 / 百万文档 tokens

## 实验结果

- 测试数据：代码库、小说、ArXiv 论文、科学论文
- 最佳配置：Gemini Text 004 或 Voyage embedding + top-20 chunks
- Reranking：Cohere reranker

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-5.png]]

## 相关概念

- [[rag]] — 基础架构
- [[embedding]] — 向量化技术
- [[bm25]] — 精确匹配
- [[reranking]] — 二次排序
- [[prompt-caching]] — 成本优化
