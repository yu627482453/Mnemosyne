---
title: "Routing"
layer: L3
kind: concept
processing_path: AI技术/Agent
updated: 2026-06-25
source: [3000-Agent/building-effective-agents.md]
tags: [routing, classification, workflow-branching, specialized-handlers, agent-patterns]
status: published
summary: 将输入分类并路由到专门处理流程的模式。通过分类器识别输入类型，分发到优化的专门 prompt。实现关注点分离，避免单一 prompt 需同时优化多任务。
---

## 定义

Routing 通过分类器将输入导向不同的专门化处理流程。

## 核心机制

```
输入 → 分类器 → 路由 → 专门处理器A/B/C → 输出
```

## 使用场景

✅ 客服系统（账单/技术/咨询）、内容处理（文章/代码/数据）
❌ 任务类型无法清晰区分

## 关系

可与 [[prompt-chaining]] 组合，属于 [[agentic-workflow]] 的一部分。

源自：[[building-effective-agents]]
