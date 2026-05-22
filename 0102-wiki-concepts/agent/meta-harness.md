---
title: "Meta-Harness"
layer: L3
kind: concept
processing_path: "3000-Agent → 0102-wiki-concepts/agent/meta-harness"
updated: 2026-05-22
source:
  - "3000-Agent/scaling-managed-agents.md"
tags:
  - agent-architecture
  - AI
  - LLM
  - infrastructure
summary: >
  Meta-Harness 是一种 agent 系统设计哲学：不对具体 harness 实现做假设，只定义 session、sandbox、
  工具调用的通用接口，使系统能容纳未来任意类型的 harness（如 Claude Code、领域专用 agent harness
  等）。其灵感来自操作系统的虚拟化抽象——操作系统不预测未来程序，只提供进程和文件等通用抽象。
  Meta-harness 对接口形状有明确意见，对接口背后的实现不作假设。
---

## 定义

Meta-Harness 是 Anthropic Managed Agents 的整体设计哲学：构建一个 agent 运行平台，其接口足够通用，能容纳"尚不存在的 harness"。它不是某个特定的 agent 循环实现，而是一组稳定接口（session、sandbox、tool）的定义，允许不同 harness 实现（Claude Code、任务专用 agent 等）接入同一个平台。

## 灵感来源

借鉴操作系统的设计原则（引自 [The Art of Unix Programming](http://www.catb.org/esr/writings/taoup/html/ch03s01.html)）：

> 操作系统通过将硬件虚拟化为抽象——进程、文件——来为"尚不存在的程序"设计系统。`read()` 不关心底层是 1970 年代的磁盘还是现代 SSD。上层抽象保持稳定，下层实现自由变更。

Meta-Harness 将同样思路应用于 agent 系统：session、harness、sandbox 是虚拟化后的抽象，各自可以独立替换实现。

## 核心原则

1. **对接口形状有意见，对实现无假设**：定义 `execute()`, `getEvents()`, `provision()` 等接口，但不限制 sandbox 是容器、手机还是其他形式
2. **harness 可替换**：Claude Code 是当前出色的 harness，但平台允许任务专用的 agent harness 并存
3. **适应模型能力演进**：当模型行为变化（如 Opus 4.5 不再有"上下文焦虑"），harness 可以独立更新，不需要改动 session 或 sandbox

## 与具体 Harness 的关系

| 类型 | 例子 | 适用场景 |
|------|------|----------|
| 通用 harness | Claude Code | 广泛任务 |
| 领域专用 harness | 代码审查 agent、部署 agent | 狭窄领域，优化特定工作流 |
| 未来 harness | 未知 | 由接口的通用性保证兼容 |

## 来源

- [[scaling-managed-agents]]
- <https://www.anthropic.com/engineering/managed-agents>
