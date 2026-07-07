---
title: "语义相似度（Semantic Similarity）"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: 2026-07-07
source: ["待补充"]
tags: [semantic-similarity, embedding, cosine-similarity, vector-search, neural-retrieval]
status: draft
summary: "语义相似度是衡量文本语义层面相近程度的方法，通过向量嵌入将文本映射到高维向量空间，再计算向量间的距离（如余弦相似度）来量化语义接近程度。与基于词频的传统方法不同，语义相似度能捕捉深层语义关系，即使表述完全不同的文本也能识别语义相近性。是现代RAG系统和语义检索的核心技术。"
---

## 定义

语义相似度通过向量嵌入技术，在语义层面衡量文本间的相近程度，突破词汇匹配的局限。

## 核心机制

- **向量嵌入**：将文本映射到高维向量空间
- **相似度计算**：余弦相似度、欧氏距离等
- **语义理解**：捕捉深层语义关系

## 相关概念

- [[embedding]] - 向量嵌入技术
- [[vector-database]] - 向量数据库
