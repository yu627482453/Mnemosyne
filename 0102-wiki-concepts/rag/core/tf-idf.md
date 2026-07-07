---
title: "TF-IDF（词频-逆文档频率）"
layer: L3
kind: concept
processing_path: "AI技术/RAG与检索"
updated: 2026-07-07
source: ["待补充"]
tags: [tf-idf, information-retrieval, bm25, keyword-extraction, text-analysis]
status: draft
summary: "TF-IDF（Term Frequency-Inverse Document Frequency）是信息检索领域的经典统计方法，用于评估词语对文档的重要程度。TF部分衡量词频，IDF部分衡量稀有度，两者结合可识别对文档最具区分性的词语。广泛应用于文档检索、关键词提取和文本相似度计算，是BM25等现代检索算法的基础。TF-IDF值越高，说明该词对文档越重要且越具区分性。"
---

## 定义

TF-IDF结合词频（Term Frequency）和逆文档频率（Inverse Document Frequency），用于评估词语对文档的重要性和区分性。

## 核心机制

- **TF(t,d)**：词t在文档d中的出现频率
- **IDF(t)**：log(文档总数/包含词t的文档数)
- **TF-IDF(t,d) = TF(t,d) × IDF(t)**

高频且稀有的词获得高权重。

## 相关概念

- [[bm25]] - TF-IDF的改进版本
