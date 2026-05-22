---
title: "Managed Agents"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3001-Agent/managed-agents.md"]
tags: [AI, LLM, Agent, Agent架构, 上下文工程, 基础设施, 综述]
status: draft
summary: "Managed Agents 是 Anthropic 在 Claude Platform 上提供的托管式长时间运行代理服务。其核心架构将代理系统虚拟化为三个独立接口：Session（持久事件日志）、Harness（调用 Claude 并路由工具调用的循环）、Sandbox（代码执行环境）。设计哲学借鉴操作系统——接口足够通用以容纳未来的实现。关键模式包括：脑手分离（Brain-Hands decoupling），Harness 和容器均为无状态 Cattle 可替换；Session 作为上下文窗口外部的持久上下文对象，支持 getEvents() 回溯；凭证通过 token 注入和 MCP vault 代理与沙箱隔离。架构收益包括 TTFT 大幅下降（p50 约 60%，p95 超 90%）和多脑多手灵活扩展。"
---

# Managed Agents

## 定义

Managed Agents 是 Anthropic Claude Platform 提供的托管式代理服务，通过将代理系统的 Brain（推理与循环）、Hands（执行环境与工具）、Session（事件日志）虚拟化为独立接口，实现可恢复、安全、可扩展的长时间运行代理。

## 解释

### 架构三组件

| 组件 | 接口 | 职责 |
|------|------|------|
| **Session** | `getEvents()`, `emitEvent()` | 持久事件日志，位于 Harness 外部，支持回溯和恢复 |
| **Harness** | `wake(sessionId)`, `getSession(id)` | 无状态代理循环，调用 Claude 并路由工具调用 |
| **Sandbox** | `execute(name, input) → string`, `provision({resources})` | 代码执行环境，按需创建，故障可替换 |

### Pets vs Cattle

传统耦合架构中，容器承载 Session + Harness + Sandbox，成为需人工护理的 Pet。解耦后三者均变为 Cattle——任一组件故障可自动替换恢复：

- 容器故障 → Harness 捕获为工具调用错误 → Claude 决定重试 → 新容器 `provision()` 
- Harness 崩溃 → `wake(sessionId)` 重启 → `getSession(id)` 加载事件日志 → 从最后事件恢复

### 安全模型

凭证与沙箱结构性隔离，两种互补模式：

1. **Token 注入**（如 Git）：初始化时将 repo token 写入本地 remote，沙箱内操作无需感知 token
2. **Vault 代理**（如 MCP）：OAuth token 存于外部保险柜，Harness 通过专用代理调用，Claude 和 Harness 均不接触凭证

### Session ≠ 上下文窗口

Session 是上下文窗口外部的持久对象，`getEvents()` 支持按位置切片、回退重读、断点恢复。Context engineering（compaction/trimming/organization）由 Harness 自由编码，Session 仅保证持久性和可查询性。

## 关键引用

- [[managed-agents]] — Anthropic Engineering Blog 原文，脑手分离架构的完整介绍

## 相关概念

- [[building-effective-agents]] — 构建有效代理的设计原则
- [[context-engineering]] — 上下文工程和窗口管理技术
- [[claude-code-harness]] — Claude Code 作为具体 Harness 实现
- [[pets-vs-cattle]] — 基础设施设计模式

## 争议与分歧

<!-- 单来源，暂无争议 -->
