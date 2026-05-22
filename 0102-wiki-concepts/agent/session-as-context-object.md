---
title: "Session as Context Object"
layer: L3
kind: concept
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
tags: [AI, context-engineering, session-management, agent-architecture, managed-agents]
status: draft
summary: >
  Session 作为 Context Window 外部的持久化上下文对象，是 Managed Agents 的核心设计之一。
  区别于传统的 compaction/trimming 等不可逆上下文管理手段，Session 通过 getEvents() 接口
  支持按位置切片检索事件流，允许 Brain 回溯、重读和断点恢复。Session 仅保证持久性和可
  查询性，具体上下文工程（压缩、组织、缓存优化）交由 Harness 自由编码。这种关注点分离使得
  上下文管理策略可以随模型能力演进而无需修改 Session 层。
---

# Session as Context Object

## 定义

Session 作为 Context Window 外部的持久化上下文对象，通过 getEvents() 支持按位置切片回溯，与 Harness 中的上下文工程解耦。

## 解释

长时间任务超出上下文窗口时，compaction/trimming 涉及不可逆的保留/丢弃决策。Session 将上下文持久化在外部日志中，Harness 可按需通过 getEvents() 检索任意位置事件，支持断点恢复和回退重读。

## 关键引用
- [[scaling-managed-agents]]（L2）

## 相关概念
- [[brain-hands-decoupling]] — 脑手分离
- [[meta-harness]] — 元 Harness
- [[context-engineering]] — 上下文工程
