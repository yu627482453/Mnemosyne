---
title: "Managed Agents"
layer: L3
kind: entity
entity_type: Product
updated: 2026-05-22
source:
  - "3000-Agent/scaling-managed-agents.md"
tags:
  - managed-agents
  - AI
  - LLM
  - agent-architecture
  - anthropic
summary: >
  Managed Agents 是 Anthropic Claude Platform 上的托管长时域 agent 运行服务。它将 agent 系统
  虚拟化为三个独立接口——Session（只追加事件日志）、Harness（调用 Claude 并路由 tool call 的循环）、
  Sandbox（代码执行环境）。核心设计理念是 Brain-Hands Decoupling：harness 不驻留在容器内，通过
  execute(name, input) → string 接口调用所有工具。支持按需 provisioning、harness 无状态重启、
  token 不进入 sandbox 的安全隔离，以及多 brain 多 hand 横向扩展。
---

## 概述

Managed Agents 是 Anthropic 提供的托管式 agent 运行平台，用户通过 Claude Platform API 提交任务，平台负责 agent 的完整生命周期管理。

## 架构

```
+-------------------------------------------+
|            Managed Agents                   |
|  +---------+  +----------+  +--------+     |
|  | Session  |  | Harness  |  |Sandbox |     |
|  |(事件日志)|  |(推理循环)|  |(执行环境)|    |
|  +---------+  +----------+  +--------+     |
|       ^            ^              ^          |
|       +------------+--------------+          |
|            稳定接口分离                       |
+-------------------------------------------+
```

## 关键接口

| 接口 | 签名 | 用途 |
|------|------|------|
| 唤醒 | `wake(sessionId)` | 重启崩溃的 harness |
| 读取 | `getSession(id)` | 获取 session 事件日志 |
| 写入 | `emitEvent(id, event)` | 追加事件到 session log |
| 查询 | `getEvents()` | 按位置切片检索上下文 |
| 执行 | `execute(name, input) → string` | 调用 sandbox/工具 |
| 供应 | `provision({resources})` | 创建新的执行环境 |

## 性能

解耦架构后：
- p50 TTFT 下降约 60%
- p95 TTFT 下降超 90%

## 安全性

- Auth token 永不进入 sandbox
- Git 仓库在 sandbox 初始化时用 token 克隆
- MCP 工具通过代理调用，token 存储在外部 vault
- Harness 不接触任何凭据

## 来源

- [[scaling-managed-agents]]
- 官方文档: <https://platform.claude.com/docs/en/managed-agents/overview>
- <https://www.anthropic.com/engineering/managed-agents>
