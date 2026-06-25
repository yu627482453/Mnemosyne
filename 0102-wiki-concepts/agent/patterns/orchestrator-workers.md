---
title: "Orchestrator-Workers"
layer: L3
kind: concept
processing_path: AI技术/Agent
updated: 2026-06-25
source: [3000-Agent/building-effective-agents.md]
tags: [orchestrator-workers, multi-agent, task-decomposition, parallel-execution, agent-patterns]
status: published
summary: 中心 LLM 动态分解任务并委派给工作 LLM，最后综合结果。适用于子任务不可预测的复杂场景，支持并行化和重试。
---

## 定义

中心编排器动态分解任务，委派给工作器，综合结果。

## 核心机制

```
任务 → 编排器分解 → 并行工作器 → 综合
```

## 使用场景

✅ 子任务不可预测、可并行、需重试

源自：[[building-effective-agents]]
