---
title: "Agent vs Workflow（智能体与工作流）"
layer: L3
kind: comparison
comparison_axis: "orchestration-control"
lhs: "Agent"
rhs: "Workflow"
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - agent-architecture
  - workflow-patterns
  - system-design
  - autonomy
  - predictability
  - agentic-systems
  - orchestration
status: published
summary: "Anthropic 将所有 LLM 驱动的系统统称为 agentic systems，但做了重要的架构区分：Workflows 是 LLM 和工具通过预定义代码路径进行编排的系统；Agents 是 LLM 动态指导自身流程和工具使用的系统，保持对任务完成方式的控制权。两者不是替代关系而是互补关系，选择标准在于任务的确定性和灵活性。Workflow 为定义明确的任务提供可预测性和一致性；Agent 在需要灵活性和模型驱动决策的场景中更合适。Anthropic 的核心建议是从最简方案开始，仅在有明确收益时才增加复杂度，对于许多应用单次 LLM 调用加检索和上下文示例通常就足够了。"
---

## 对比维度

**编排控制方式**（orchestration-control）：系统如何决定执行流程和工具调用顺序。

## LHS: Agent（智能体）

- **控制方式**：LLM 动态指导自身流程和工具使用
- **执行路径**：运行时由模型决策，非预定义
- **灵活性**：高，适应开放性问题
- **可预测性**：低，输出和路径不确定
- **适用场景**：步骤数不可预测、需要模型驱动决策的开放任务
- **风险**：更高成本和错误复合的可能性
- **保护机制**：需要 sandbox 测试和 guardrails

## RHS: Workflow（工作流）

- **控制方式**：通过预定义代码路径编排
- **执行路径**：开发时硬编码，运行时确定
- **灵活性**：低，按固定模式执行
- **可预测性**：高，输出稳定一致
- **适用场景**：定义明确的任务，需要一致性和可控性
- **代表模式**：[[prompt-chaining]]、[[routing]]、[[parallelization]]、[[orchestrator-workers]]、[[evaluator-optimizer]]

## 选择原则

1. **复杂度最小化**：从最简方案开始，仅在有明确收益时才增加复杂度
2. **单次调用优先**：对于许多应用，单次 LLM 调用 + RAG 通常就足够了
3. **互补而非替代**：两者不是替代关系，而是根据任务特性选择

## 复杂度谱系

```
单次 LLM 调用 → Workflow（5 种模式）→ 自主 Agent
     ↑                    ↑                    ↑
  最简方案           中等复杂度           最高复杂度
```

## 相关概念

- [[augmented-llm]]
- [[tool-engineering]]
