---
title: "SWE-bench"
layer: L3
kind: entity
entity_type: Project
processing_path: "AI技术/Agent"
updated: 2026-06-25
source:
  - "3000-Agent/building-effective-agents.md"
tags:
  - swe-bench
  - benchmark
  - coding-agent
  - github-issues
  - autonomous-coding
  - evaluation
status: published
summary: "SWE-bench 是一个评估自主编码 Agent 能力的基准测试项目，包含从真实 GitHub 仓库收集的 issue。Agent 需要仅基于 pull request 描述自主编辑多个文件来解决问题。Anthropic 的 SWE-bench agent 在 SWE-bench Verified 基准上展示了强大的自主编码能力，能够解决真实的 GitHub issue。SWE-bench 是 coding agent 领域的重要评估工具，验证了 agent 在开放性问题上的自主决策和多文件编辑能力。该基准测试体现了 coding agent 的核心特征：解决方案可通过自动化测试验证，agent 可使用测试结果作为反馈迭代改进。"
---

## 基本信息

SWE-bench 是评估自主编码 Agent 能力的基准测试项目，包含从真实 GitHub 仓库收集的 issue。

## 核心特征

- **真实问题**：从真实 GitHub 仓库收集 issue，反映实际开发场景
- **自主解决**：Agent 仅基于 pull request 描述自主编辑多个文件
- **可验证性**：解决方案可通过自动化测试验证
- **迭代改进**：Agent 可使用测试结果作为反馈迭代改进

## 在 Agent 研究中的意义

- **评估自主性**：验证 agent 在开放性问题上的自主决策能力
- **多文件编辑**：测试 agent 处理复杂跨文件变更的能力
- **工具使用**：评估 agent 使用编码工具（如文件编辑、测试运行）的可靠性

## Anthropic 的实践

Anthropic 的 SWE-bench agent 在 SWE-bench Verified 基准上展示了强大的自主编码能力，能够解决真实的 GitHub issue。在构建该 agent 时，Anthropic 发现工具优化的时间远超 prompt 优化时间，这一发现推动了 [[tool-engineering]] 方法论的发展。

## 相关概念

- [[tool-engineering]]
- [[agent-vs-workflow]]
- [[evaluator-optimizer]]
