---
title: "Meta-Harness"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
tags: [AI, agent-architecture, meta-harness, managed-agents, infrastructure]
status: draft
summary: >
  Meta-Harness 是对具体 Harness 实现不做假设、只定义通用接口的代理编排层设计理念。借鉴操作
  系统将硬件虚拟化为 read/write/process 等通用抽象的思路，Managed Agents 将 Agent 组件虚
  拟化为 Session（事件日志）、Harness（推理循环）、Sandbox（执行环境）三个接口。Claude Code
  和领域专用 Harness 均可作为实现接入，接口稳定而实现可自由替换。这种设计使系统能适应未来
  模型能力的演进，不被当前 Harness 假设所束缚。
---

# Meta-Harness

## 定义

Meta-Harness 是一种 Agent 编排层的设计哲学：对具体 Harness 实现保持无立场，仅定义通用接口（Session/Harness/Sandbox），使不同 Harness 实现可互换接入。

## 解释

类比操作系统：read() 不关心底层是 1970 年代的磁盘还是现代 SSD。Managed Agents 定义 execute()、wake()、emitEvent() 等接口，不规定具体 Harness 形态——Claude Code、领域专用 Agent 均可运行。

## 关键引用
- [[scaling-managed-agents]]（L2）

## 相关概念
- [[brain-hands-decoupling]] — 脑手分离架构
- [[session-as-context-object]] — Session 设计
