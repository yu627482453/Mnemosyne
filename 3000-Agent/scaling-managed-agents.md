---
id: "f44cb74c"
title: "Scaling Managed Agents: Decoupling the brain from the hands"
topic: "3000-Agent"
layer: L2
kind: standard
tags: [AI, LLM, agent-architecture, context-engineering, infrastructure, sandbox, managed-agents, session-management]
aliases: ["Managed Agents 架构", "Brain-Hands Decoupling"]
created: 2026-05-22
updated: 2026-05-22
source: url
source_url: "https://www.anthropic.com/engineering/managed-agents"
resource_refs:
  - "0001-resource/3000-Agent/scaling-managed-agents/20260522-1.png"
  - "0001-resource/3000-Agent/scaling-managed-agents/20260522-2.png"
  - "0001-resource/3000-Agent/scaling-managed-agents/20260522-3.png"
  - "0001-resource/3000-Agent/scaling-managed-agents/20260522-4.png"
content_hash: "54d6496c"
status: draft
summary: >
  Anthropic 工程博客介绍 Managed Agents 的架构设计理念——将 agent 系统的"大脑"（harness/推理循环）
  与"双手"（sandbox/工具执行环境）解耦。核心思路借鉴操作系统的虚拟化抽象：通过稳定接口（session、
  harness、sandbox）替代单体耦合设计，使各组件可独立替换和扩缩容。文章阐述了四个关键主题：(1) 从
  pets 到 cattle 的基础设施演进——harness 和容器都可无状态重启；(2) 安全边界重构——auth token 永
  不暴露在 sandbox 内；(3) session 作为 context window 之外的持久化上下文对象；(4) 多 brain 多
  hand 的横向扩展能力。解耦后 p50 TTFT 下降约 60%，p95 下降超 90%。整体定位为"元 harness"——
  对具体 harness 实现不做假设，只定义通用接口，以适应未来模型能力的演进。
---
