---
title: "Claude Code"
layer: L3
kind: entity
entity_type: "Product"
updated: 2026-05-21
source: [3002-LLM/claude-code-auto-mode.md]
tags: [AI, 机器学习, LLM, developer-tools, cli]
status: draft
summary: "Anthropic 官方 CLI AI 编程助手，集成 Claude 模型进行代码生成、调试与重构。支持 Auto Mode 自动权限决策，通过输入层 probe 与输出层 classifier 共同约束执行风险。定位为终端内 AI 编程代理，区别于 Web Chat 和 API 调用两种交互方式，适用于本地开发、CI 集成与多 agent 编排场景。"
---

# Claude Code

## 基本信息

| 属性 | 内容 |
|------|------|
| 名称 | Claude Code |
| 类型 | Product |
| 开发商 | Anthropic |
| 定位 | 终端内 AI 编程助手 |

## 关键事实

- Anthropic 推出的官方 CLI 工具
- 支持 Auto Mode：通过分类器减少权限弹窗并保留安全边界
- [[claude-code-auto-mode]] — 自动模式的概念说明

## 关联

- [[claude-code-auto-mode]] — 自动模式运作机制
- [[sandbox-vs-skip-permissions-vs-auto-mode]] — 三种权限模式对比
