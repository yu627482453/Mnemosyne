---
title: "Brain-Hands Decoupling"
layer: L3
kind: concept
processing_path: "3000-Agent → 0102-wiki-concepts/agent/brain-hands-decoupling"
updated: 2026-05-22
source:
  - "3000-Agent/scaling-managed-agents.md"
tags:
  - agent-architecture
  - AI
  - LLM
  - infrastructure
summary: >
  Brain-Hands Decoupling 是一种 agent 系统架构模式：将"大脑"（LLM 推理 + harness 循环）与
  "双手"（sandbox、工具、执行环境）通过稳定接口分离。核心接口为 execute(name, input) → string，
  使 harness 对执行环境无感知——sandbox 可以是容器、手机或任何可执行环境。解耦收益包括：(1) 组件
  独立故障恢复——harness 和 sandbox 都变为 cattle，可无状态重启；(2) 安全边界清晰——token 不进入
  sandbox；(3) 按需 provisioning——减少 TTFT；(4) 多 brain 多 hand 横向扩展。
---

## 定义

Brain-Hands Decoupling（大脑-双手解耦）是 Anthropic Managed Agents 的核心架构模式。它将 agent 系统拆分为三个通过稳定接口通信的独立组件：

| 组件 | 角色 | 接口 |
|------|------|------|
| **Brain** | Claude + harness 推理循环 | `wake(sessionId)`, `getSession(id)`, `emitEvent(id, event)` |
| **Hands** | sandbox / 工具执行环境 | `execute(name, input) → string`, `provision({resources})` |
| **Session** | 持久化事件日志 | `getEvents()` |

## 关键属性

- **无状态性**：harness 不持有任何需要存活的状态——崩溃后可通过 session log 恢复
- **工具无关性**：harness 不知道 sandbox 的具体实现，所有工具统一为 `execute(name, input) → string`
- **按需 provisioning**：sandbox 仅在实际需要时才创建，不阻塞推理启动
- **安全隔离**：auth token 存储在 sandbox 外部（vault / 资源绑定），沙箱内代码无法访问

## 与单体架构的对比

| 维度 | 单体容器 | 解耦架构 |
|------|----------|----------|
| 故障恢复 | 容器故障 = session 丢失 | harness/sandbox 独立重启 |
| 安全 | token 与 untrusted code 同容器 | token 永不进入 sandbox |
| 启动延迟 | 每 session 完整容器启动 | 按需 provisioning |
| 扩展 | 1 brain : 1 container | N brains : M hands |
| 调试 | 需进入含用户数据的容器 | 组件独立可观测 |

## 来源

- [[scaling-managed-agents]]
- <https://www.anthropic.com/engineering/managed-agents>
