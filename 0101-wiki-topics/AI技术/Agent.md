---
title: "Agent 主题综述"
layer: L3
kind: topic
processing_path: "AI技术/Agent"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
tags: [AI, agent-architecture, managed-agents, infrastructure, context-engineering]
status: draft
summary: >
  Agent 主题域涵盖 AI Agent 系统的架构设计、编排模式与工程实践。当前收录 Anthropic Managed
  Agents 的脑手分离架构设计，涉及Session 持久化、Harness 无状态化、Sandbox Cattle 化、
  安全边界结构性隔离等关键模式。该域后续可扩展至多 Agent 协作、Agent 评估、上下文工程等方向。
---

# Agent

## 概述

Agent 主题域聚焦 AI Agent 系统的架构设计与工程实践，当前以 Anthropic Managed Agents 的脑手分离架构为核心入口。

## 概念目录
- [[brain-hands-decoupling]] — 脑手分离架构模式
- [[meta-harness]] — 元 Harness 设计理念
- [[session-as-context-object]] — Session 作为上下文对象

## 实体目录
- [[0103-wiki-entities/product/managed-agents|Managed Agents]] — Anthropic 托管式 Agent 服务

## 对比目录
- [[0104-wiki-comparisons/agent-architecture/session-vs-context-window|Session Log vs Context Window]] — 两种上下文管理策略
