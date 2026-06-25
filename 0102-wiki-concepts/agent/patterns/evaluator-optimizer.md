---
title: "Evaluator-Optimizer"
layer: L3
kind: concept
processing_path: AI技术/Agent
updated: 2026-06-25
source: [3000-Agent/building-effective-agents.md]
tags: [evaluator-optimizer, iterative-refinement, feedback-loop, quality-improvement, agent-patterns]
status: published
summary: 一个 LLM 生成，另一个评估反馈的循环模式。通过迭代优化提升输出质量，适用于有明确评估标准的场景。
---

## 定义

生成器-评估器循环迭代直到达到质量标准。

## 核心机制

```
任务 → 生成 → 评估 → 反馈 → 生成 → ...
```

## 使用场景

✅ 明确评估标准、迭代价值可衡量

源自：[[building-effective-agents]]
