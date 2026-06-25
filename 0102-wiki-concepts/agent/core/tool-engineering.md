---
title: "Tool Engineering（工具工程）"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - tool-engineering
  - aci
  - tool-design
  - prompt-engineering
  - poka-yoke
  - interface-design
status: published
summary: "Tool Engineering 是 Anthropic 提出的核心概念，强调工具定义和规范应获得与整体 prompt 同等的 prompt engineering 关注。提出 ACI（Agent-Computer Interface）概念，将 HCI（Human-Computer Interface）的设计思维迁移到 agent 工具接口上。Anthropic 在 SWE-bench agent 实践中，花在优化工具上的时间比整体 prompt 更多。关键设计原则包括：给模型足够 token 在陷入死角前思考；保持格式接近训练数据中自然出现的格式；消除格式开销（如准确计数行数或转义代码）；站在模型角度思考工具是否直观易用；进行 Poka-yoke 防错设计。一个反直觉发现是：将相对文件路径改为绝对路径后，模型完美使用了这种方法。"
---

## 定义

Tool Engineering 是 Anthropic 提出的工具设计方法论，强调工具定义应获得与 prompt 同等的工程关注，提出 ACI（Agent-Computer Interface）概念。

## ACI 概念

ACI（Agent-Computer Interface）将 HCI（Human-Computer Interface）的设计思维迁移到 agent 工具接口上。Anthropic 建议在 ACI 上投入与 HCI 同等的精力。

## 核心设计原则

### 格式选择

- 给模型足够 token 在"陷入死角"之前"思考"
- 保持格式接近模型在训练数据中自然出现的格式
- 确保没有格式"开销"（如准确计数数千行代码或转义代码）

### 接口设计

- **直观性**：站在模型角度思考，基于描述和参数是否显而易见如何使用
- **文档化**：好的工具定义包括示例用法、边界情况、输入格式要求、与其他工具的清晰边界
- **命名清晰**：考虑如何更改参数名称或描述使事情更直观，如同为初级开发者写文档字符串

### 测试与防错

- **迭代测试**：在工作台中运行大量示例输入，查看模型犯什么错误，然后迭代
- **Poka-yoke**：改变参数使错误更难发生（防错设计）

## SWE-bench 实践经验

Anthropic 在构建 SWE-bench agent 时，花在优化工具上的时间比整体 prompt 更多。一个关键发现：模型在使用相对文件路径的工具时会在 agent 离开根目录后犯错，改为始终要求绝对文件路径后，模型完美使用了这种方法。

## 与其他概念的关系

- 是 [[augmented-llm]] 的关键组成部分
- 直接影响 [[agent-vs-workflow]] 中 agent 的可靠性
- 工具设计质量决定 agent 的成功率

## 相关概念

- [[augmented-llm]]
- [[agent-vs-workflow]]
