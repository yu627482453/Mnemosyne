---
title: "Prompt Chaining"
layer: L3
kind: concept
processing_path: AI技术/Agent
updated: 2026-06-25
source: [3000-Agent/building-effective-agents.md]
tags: [prompt-chaining, workflow, task-decomposition, sequential-processing, agent-patterns]
status: published
summary: 将复杂任务分解为顺序步骤的工作流模式，每个 LLM 调用处理前一步输出。可添加中间检查，确保流程正确。适用于任务可清晰分解为固定子任务的场景。
---

## 定义

Prompt Chaining 将任务拆解为一系列步骤，每步由独立 LLM 调用完成，当前输出成为下一步输入。

## 核心机制

```
任务 → 步骤1 → 检查 → 步骤2 → 检查 → 结果
```

## 使用场景

✅ 代码生成→审查→修订、文档分析→总结→翻译
❌ 步骤无法预先确定、需动态分支

## 关系

基于 [[augmented-llm]]，可与 [[routing]] 结合。

源自：[[building-effective-agents]]
