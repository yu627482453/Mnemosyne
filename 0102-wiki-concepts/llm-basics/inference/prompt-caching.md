---
title: "Prompt Caching：提示词缓存"
layer: L3
kind: concept
processing_path: "AI技术/LLM基础"
updated: "2026-06-26"
source: [3001-RAG与检索/contextual-retrieval.md]
tags: [prompt-caching, cost-optimization, latency-reduction, claude-feature, cache-reuse, api-optimization, token-savings, inference-acceleration]
status: draft
summary: "Prompt Caching 是 Claude API 的缓存功能，在多次调用间复用相同提示词内容，延迟降低 >2 倍、成本降低高达 90%。工作原理：首次调用将长提示词加载到缓存（TTL 5分钟），后续调用复用缓存。特别适合 RAG 场景：小知识库（<200k tokens）直接放入提示词配合缓存；Contextual Retrieval 中用于降低上下文生成成本（完整文档缓存一次，处理每个 chunk 时复用），成本仅 $1.02/百万文档 tokens。适用场景：系统指令长、知识库固定、批量处理。"
---

# Prompt Caching：提示词缓存

## 定义

**Prompt Caching** 是 Claude API 提供的缓存功能，在多次调用间复用相同提示词内容，降低延迟和成本。

## 性能提升

- **延迟**：降低 >2 倍
- **成本**：降低高达 90%
- **缓存 TTL**：5 分钟

## 工作原理

```
首次调用：长提示词 → 处理 → 加载到缓存 → 生成响应
后续调用：标记缓存 → 直接复用 → 仅处理新内容
```

## 在 RAG 中应用

### 小知识库（< 200k tokens）

直接将整个知识库放入提示词 + 缓存，无需复杂 [[rag]] 架构。

### Contextual Retrieval

为每个 chunk 生成上下文时：
```xml
<document>{{完整文档}}</document>  ← 缓存一次
<chunk>{{chunk1}}</chunk>  ← 每次不同
```

**成本**：$1.02 / 百万文档 tokens

## 适用场景

✅ 系统指令长、知识库固定、批量处理  
❌ 提示词频繁变化、单次调用

## 相关概念

- [[contextual-retrieval]] — 成本优化应用
- [[rag]] — 替代方案（小知识库）
