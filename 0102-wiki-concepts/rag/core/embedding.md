---
title: "Embedding：向量嵌入"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
source: [3001-RAG与检索/contextual-retrieval.md]
tags: [embedding, vector-representation, semantic-search, dense-retrieval, cosine-similarity, embedding-model, gemini-embedding, voyage-embedding]
status: draft
summary: "Embedding 将文本转换为高维向量表示，使计算机通过数值计算理解语义。在 RAG 中用于将文档块和查询编码为向量，通过余弦相似度找到语义相关内容。能捕获同义词、上下文关系。主流模型：Gemini Text 004（768维）、Voyage（1024维）、OpenAI Ada 002（1536维）。Contextual Retrieval 实验中，Gemini 和 Voyage 对上下文化 chunks 表现最佳。局限：可能错过精确匹配（如错误代码），需结合 BM25 混合检索。需向量数据库（Pinecone、Weaviate）存储和检索。"
---

# Embedding：向量嵌入

## 定义

**Embedding** 将文本映射到连续向量空间，使语义相似文本在向量空间中彼此接近。

```
"汽车" → [0.23, -0.45, 0.78, ...]  (768维)
"车辆" → [0.25, -0.43, 0.76, ...]  (相似向量)
```

## 在 RAG 中应用

**预处理**：文档 → 切块 → Embedding → [[vector-database]]  
**查询**：用户输入 → Embedding → 向量检索(KNN) → Top-K

## 优势与局限

✅ 语义理解、跨语言、模糊匹配  
❌ 精确匹配弱（错误代码、订单号）、计算密集

## 主流模型

| 模型 | 维度 | 特点 | 成本 |
|------|------|------|------|
| Gemini Text 004 | 768 | 高质量、多语言 | $0.025/1M |
| [[voyage-ai]] | 1024 | RAG 优化 | $0.12/1M |
| OpenAI Ada 002 | 1536 | 通用稳定 | $0.13/1M |

## Contextual Embeddings

[[contextual-retrieval]] 改进：chunk + 上下文说明 → Embedding  
**效果**：检索失败率 ↓35%（5.7% → 3.7%）

## 相关概念

- [[rag]] — 应用场景
- [[semantic-similarity]] — 检索依据
- [[bm25]] — 互补技术
- [[contextual-retrieval]] — 优化方法
