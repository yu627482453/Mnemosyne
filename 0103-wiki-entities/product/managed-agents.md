---
title: "Managed Agents"
layer: L3
kind: entity
entity_type: "Product"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
tags: [AI, managed-agents, agent-architecture, infrastructure, product]
status: draft
summary: >
  Managed Agents 是 Anthropic Claude Platform 上提供的托管式长时间运行 Agent 服务。核
  心设计将 Agent 虚拟化为 Session（事件日志）、Harness（推理循环）、Sandbox（执行环境）
  三个独立接口，借鉴操作系统虚拟化思想。支持脑手分离、故障自动恢复、凭证与沙箱结构性
  隔离。TTFT 中位数下降约 60%，支持多脑多手灵活扩展。定位为元 Harness——对具体 Harness
  实现不做假设，可容纳 Claude Code 和领域专用 Agent 等多种形态。
---

# Managed Agents

## 基本信息

| 属性 | 内容 |
|------|------|
| 名称 | Managed Agents |
| 类型 | Product |
| 开发商 | Anthropic |
| 定位 | Claude Platform 托管式 Agent 服务 |

## 关键事实
- [[scaling-managed-agents]]（L2）— Anthropic 工程博客
- 核心接口：Session (getEvents/emitEvent)、Harness (wake/getSession)、Sandbox (execute/provision)

## 关联
- [[brain-hands-decoupling]] — 脑手分离架构
- [[meta-harness]] — 元 Harness
- [[session-as-context-object]] — Session 设计
