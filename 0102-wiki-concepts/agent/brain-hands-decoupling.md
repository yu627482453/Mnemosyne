---
title: "Brain-Hands Decoupling"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
planned_links: ['pets-vs-cattle']
tags: [AI, agent-architecture, infrastructure, brain-hands-decoupling, managed-agents]
status: draft
summary: >
  将 Agent 系统的 Brain（Claude+Harness）与 Hands（Sandbox+Tools）解耦为独立接口的架构模式。
  Harness 通过 execute(name, input) 调用沙箱，容器从 Pet 变为 Cattle——故障可自动替换恢复。
  Session 作为外部持久事件日志支持 wake() 恢复。解耦后 TTFT 中位数下降约 60%，p95 超 90%。
  安全上凭证永不进入沙箱，通过 token 注入和 MCP vault 代理实现结构性隔离。该模式使 Harness
  不再对执行环境做假设，支持多脑多手灵活扩展。
---

# Brain-Hands Decoupling

## 定义

Brain-Hands Decoupling 是将 Agent 系统的推理决策层（Brain）与执行环境层（Hands）通过稳定接口分离的架构模式，核心接口为 execute(name, input) → string。

## 解释

传统耦合架构中 Harness 内嵌于容器，假设所有资源在容器内。解耦后三者各自独立：
- Brain（Claude + Harness）通过 execute() 调用 Hands，不感知执行环境细节
- Hands（Sandbox + Tools）变为 Cattle——故障时新容器 provision() 替换
- Session 作为 Brain 外部的持久日志，崩溃后 wake(sessionId) 恢复

## 关键引用
- [[scaling-managed-agents]]（L2）— Anthropic 工程博客原文

## 相关概念
- [[meta-harness]] — 元 Harness 设计理念
- [[session-as-context-object]] — Session 作为上下文对象
- [[pets-vs-cattle]] — Pets vs Cattle 运维模式
