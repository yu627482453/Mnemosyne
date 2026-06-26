---
title: "Reranking：检索重排序"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: "2026-06-26"
source: [3001-RAG与检索/contextual-retrieval.md]
tags: [reranking, retrieval-optimization, ranking-model, cross-encoder, rag-optimization, cohere-rerank, search-quality, precision-recall]
status: draft
summary: "Reranking 是 RAG 中的二次精排技术，对初始检索的大量候选进行过滤。流程：初检索获取 top-150 → reranking 模型打分 → 选择 top-20 传给 LLM。基于 cross-encoder 架构，比 bi-encoder 更准确但更慢。在 Contextual Retrieval 基础上加入 reranking，失败率从 2.9% 降至 1.9%（额外 34% 提升）。主流工具：Cohere Rerank、Voyage Reranker。权衡：增加运行时延迟（50-200ms）和成本（$1/1M tokens）。适合对检索质量要求高的场景。"
---

# Reranking：检索重排序

## 定义

**Reranking** 在初始检索后对候选结果二次精排，筛选最优质 top-K 传给 LLM。

## 两阶段检索

```
阶段1：[Embedding + BM25] → Top-150（快速、召回优先）
阶段2：Reranking模型 → Top-20（精准、精度优先）
```

## 架构对比

| 特性 | Bi-encoder（初检索） | Cross-encoder（Reranking） |
|------|---------------------|---------------------------|
| 速度 | 快（可预计算） | 慢（每对都需计算） |
| 准确性 | 中等 | 高 |

## 性能提升

[[contextual-retrieval]] + Reranking：失败率 2.9% → 1.9%（↓34%）

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-4.png]]

## 成本与延迟

- 成本：Cohere $1/1M tokens
- 延迟：+50-200ms

## 主流工具

- [[cohere]] Rerank API
- [[voyage-ai]] Reranker
- BGE Reranker（开源）

## 相关概念

- [[rag]] — 应用场景
- [[contextual-retrieval]] — 上游优化
- [[embedding]] / [[bm25]] — 初检索
