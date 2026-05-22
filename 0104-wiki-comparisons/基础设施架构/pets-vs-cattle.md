---
title: "Pets vs Cattle"
layer: L3
kind: comparison
comparison_axis: "基础设施架构"
lhs: "Pets（宠物）"
rhs: "Cattle（牛群）"
updated: 2026-05-22
source: ["3001-Agent/managed-agents.md"]
tags: [AI, Agent, Agent架构, 基础设施, 对比]
status: draft
summary: "Pets vs Cattle 是云计算基础设施的设计隐喻：Pet 是有名字、需人工护理、不可丢失的个体服务器；Cattle 是可互换、故障即替换的无状态实例。在代理系统架构中，耦合的容器成为 Pet（故障需人工恢复），解耦后的 Harness 和 Sandbox 变为 Cattle（崩溃自动 rebuild）。选择 Cattle 模式是实现可扩展、可恢复代理系统的基础。"
---

# Pets vs Cattle

## 对比概览

| 维度 | Pets（宠物） | Cattle（牛群） |
|------|-------------|---------------|
| 身份 | 有名字，独一无二 | 无差别，可互换 |
| 故障处理 | 人工护理、恢复 | 自动替换、rebuild |
| 状态 | 有状态，不可丢失 | 无状态，外部持久化 |
| 扩展 | 逐个纵向扩展 | 横向批量扩展 |
| 调试 | SSH 进入实例 | 日志和指标外部化 |
| 代理场景 | 耦合的单体容器 | 解耦的 Harness + Sandbox |

## 适用场景

- **选 Pets**：传统单体应用、单点部署、手工运维环境
- **选 Cattle**：云原生微服务、自动扩缩容、代理系统（Harness/Sandbox 需故障恢复）

## 依据

- [[managed-agents]] — Anthropic Managed Agents 将容器和 Harness 从 Pet 变为 Cattle，实现故障自动恢复和 p50 TTFT 下降 60%
