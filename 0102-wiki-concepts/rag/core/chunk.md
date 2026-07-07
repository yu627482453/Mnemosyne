---
title: "文本分块（Chunk）"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: 2026-07-07
source: ["待补充"]
tags: [chunk, text-splitting, rag-preprocessing, document-processing, retrieval-unit]
status: draft
summary: "文本分块是RAG系统的核心预处理步骤，将长文档切分为适合检索和生成的小段落。分块策略直接影响检索质量和生成效果。常见方法包括固定长度分块、句子边界分块、语义分块等。需要平衡块大小和重叠度以保持语义连贯性。"
---

## 定义

Chunk是将长文档切分为适合检索单元的小段落，是RAG系统的基础处理单元。

## 核心机制

- 分块策略（固定长度/句子边界/语义）
- 块大小平衡
- 重叠度设计

## 相关概念

- [[rag]]
- [[contextual-retrieval]]
