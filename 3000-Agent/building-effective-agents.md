---
id: d6011dc9
title: "Building Effective AI Agents"
topic: 3000-Agent
layer: L2
kind: standard
tags: [ai-agent, agent-design, agentic-systems, workflows, prompt-engineering, tool-use, retrieval, multi-agent]
aliases: []
created: 2026-06-25
updated: 2026-06-25
source: url
source_url: https://www.anthropic.com/research/building-effective-agents
resource_refs: []
content_hash: pending
status: draft
summary: Anthropic 官方指南，介绍构建有效 AI Agent 的核心模式和最佳实践。文章强调从简单的 workflow 开始，只在必要时增加 Agent 复杂度。核心模式包括：Augmented LLM（增强型 LLM，通过检索和工具调用扩展能力）、Prompt chaining（提示链，将任务分解为多步骤）、Routing（路由，根据输入类型分发到专门的处理流程）和 Parallelization（并行化，同时执行多个独立任务）。文章还讨论了 Orchestrator-workers 和 Evaluator-optimizer 两种多 Agent 模式，以及如何通过迭代和评估不断优化 Agent 系统。强调 Agent 是一种架构而非单一技术，成功的关键在于选择合适的复杂度层级和构建快速的评估反馈循环。
---

## 核心提炼

本文从 Anthropic 工程实践出发，提出了构建 Agent 系统的渐进式方法论：从最简单的增强型 LLM 开始，根据任务复杂度逐步引入 workflow 模式（prompt chaining、routing、parallelization），只有在需要动态适应和规划时才采用完全自主的 Agent。文章明确指出 **Agent 不是必需品**，很多场景下简单的 workflow 就能胜任。关键洞见是：复杂度应由任务需求驱动，而非技术追求；快速的评估循环比复杂的架构更重要。

## 关键概念

- [[augmented-llm]]：通过检索和工具扩展 LLM 能力
- [[prompt-chaining]]：将复杂任务分解为多个 LLM 调用的序列
- [[routing]]：根据输入类型智能分发到专门处理流程
- [[agent-loop]]：感知-思考-行动的自主循环
- [[orchestrator-workers]]：中心协调器 + 专门工作器的多 Agent 模式
- [[evaluator-optimizer]]：持续评估和优化的反馈循环

## 原文要点

### Agent 的定义与层次
- Workflows：通过预定义代码路径编排 LLM 和工具
- Agents：LLM 动态控制自身流程和工具使用
- 最佳实践：从 workflow 开始，必要时才用 agent

### 六层复杂度模型
1. Augmented LLM：基础层（检索 + 工具）
2. Prompt chaining：串行多步骤
3. Routing：条件分支路由
4. Parallelization：并发独立任务
5. Orchestrator-workers：动态任务分解
6. Evaluator-optimizer：迭代优化循环

### 核心建议
- 评估先行：定义成功标准和测试用例
- 简单优先：避免过度设计
- 人类审核：关键决策需人工确认

## 来源

- 作者：Erik Schluntz
- 机构：Anthropic
- 原文：https://www.anthropic.com/research/building-effective-agents
- 日期：2024

---

## 原文笔记

# Building effective agents

What we've learned from working with hundreds of teams building agents.

When companies first start building AI agents, there's a strong temptation to create complex systems from scratch. We've worked with hundreds of customers to build agents ranging from basic customer support chatbots to multi-agent coding systems, and we've learned one key lesson: **Start simple and add complexity only when needed.**

## What are agents?

**Workflows** are systems where LLMs and tools are orchestrated through predefined code paths.

**Agents**, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.

Both workflows and agents can be effective. The term "agents" is so broad that most discussion focuses on the more autonomous type, but **you usually want to start with workflows and use agents only when they're needed.**

## When (and when not) to build agents

When building applications with LLMs, we recommend finding the simplest solution possible. Agentic systems often trade latency and cost for better task performance.

Examples:
- **Customer support chatbot**: Predefined workflow sufficient
- **Coding agent**: Agentic system better (broad task range)

## When (and when not) to use frameworks

- **Basic workflows**: Frameworks accelerate development
- **Complex agents**: Direct API calls provide needed customization

Most customers building complex agents end up writing custom code quickly.

## Building blocks of agents

### Augmented LLM

The simplest "agentic" system augments LLM functionality with retrieval and tools. This is the most common production pattern.

**When to use:**
- Straightforward tasks in single LLM call
- Minimize latency and cost
- Avoid unnecessary complexity

### Prompt chaining

Decomposes task into sequence of steps, each LLM processing previous output. Add programmatic checks on intermediate steps.

**When to use:**
- Task cleanly decomposes into fixed subtasks
- Need programmatic validation of subtask outputs

### Routing

Classifies input and directs to specialized followup task. Enables separation of concerns and specialized prompts.

**When to use:**
- Tasks clearly separate into distinct categories
- Different inputs need fundamentally different handling

### Parallelization

Execute independent LLM calls simultaneously to save latency. Applies to both workflows and agents.

**When to use:**
- Multiple independent operations
- Reduce overall latency

### Orchestrator-workers

Central LLM dynamically breaks down tasks, delegates to workers, synthesizes results.

**When to use:**
- Complex tasks with unpredictable subtasks
- Subtasks can parallelize for speed
- Need retry until complex task achieves success

### Evaluator-optimizer

One LLM generates response while another provides evaluation and feedback in loop.

**When to use:**
- Clear evaluation criteria
- Iterative refinement provides measurable value
- Cost of multiple LLM calls acceptable

## Combining patterns

These building blocks aren't prescriptive. Most real-world applications combine several patterns. Example coding agent might use:
- Augmented LLM (code execution tools)
- Prompt chaining (break down tasks)
- Evaluator-optimizer (review and improve code)

Start simple and add complexity only as needed.

## The importance of evaluations

Recommendations:
1. **Start with evaluations before building** - Define success criteria first
2. **Measure performance constantly** - Track failures, use them to improve
3. **Test throughout development** - Don't wait until end
4. **Balance cost and quality** - Ensure performance justifies expenses

Without rigorous evaluation, you can't know if changes improve or hurt performance.

## Wrapping up

Building effective agents is about choosing the right tools for the job. Start with simple patterns, add complexity only when needed, and measure everything. The best agent is often the simplest one that gets the job done.
