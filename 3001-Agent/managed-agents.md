---
title: "Scaling Managed Agents: Decoupling the brain from the hands"
topic: "3001-Agent"
layer: L2
kind: standard
tags: [AI, LLM, Agent, Agent架构, 上下文工程, 基础设施, 综述]
aliases: [Managed Agents, 托管代理, 脑手分离架构]
created: 2026-05-22
updated: 2026-05-22
source: url
source_url: "https://www.anthropic.com/engineering/managed-agents"
resource_refs: []
status: draft
summary: "Anthropic 的 Managed Agents 是一种托管式长时间运行代理服务，核心设计借鉴操作系统虚拟化思想——将会话（Session）、Harness（代理循环）、沙箱（Sandbox）三者解耦为独立接口。文章引入 Pets vs Cattle 基础设施哲学：将 Harness 和容器都变为可替换的\"牛\"，任一故障均可恢复。解耦后，Harness 通过 execute(name, input) 接口调用沙箱，Session 作为 Harness 外部的持久事件日志，支持 wake(sessionId) 恢复和 getEvents() 灵活回溯。安全上，凭证永不进入沙箱（通过仓库 token 注入和 MCP OAuth 保险柜）。Session 不等同于 Claude 上下文窗口，而是外部上下文对象。架构收益：p50 TTFT 下降约 60%，p95 下降超 90%，并支持多脑多手灵活扩展。"
---

# Scaling Managed Agents: Decoupling the brain from the hands

## 核心内容

Anthropic 在 Claude Platform 上构建了 **Managed Agents**——一个托管式长时间运行代理服务。核心设计哲学来自操作系统：**虚拟化组件为通用接口，使实现可自由替换而接口保持稳定**。

### 问题：耦合的单体容器

初始架构将所有组件（Session、Harness、Sandbox）放入单一容器：

- 容器成为 **Pet**（宠物）而非 **Cattle**（牛）：容器故障 → Session 丢失，需人工"护理"恢复
- 调试困难：WebSocket 事件流是唯一窗口，Harness bug、网络丢包、容器离线表现相同，无法区分；进入容器调试又涉及用户数据
- Harness 内嵌假设"所有资源在容器内"，客户要接入 VPC 只能对等网络

### 方案：脑手分离

将 **Brain**（Claude + Harness）与 **Hands**（Sandbox + Tools）和 **Session**（事件日志）解耦为三个独立接口：

**Harness 离开容器。** Harness 通过 `execute(name, input) → string` 调用沙箱，容器变为 Cattle——故障时捕获为工具调用错误，Claude 可决定重试并初始化新容器 `provision({resources})`。

**Harness 故障恢复。** Session 日志位于 Harness 外部，Harness 本身也变为 Cattle。崩溃后通过 `wake(sessionId)` 重启，`getSession(id)` 获取事件日志，从最后事件恢复。

**安全边界。** 凭证永不进入沙箱。Git 访问：初始化时注入 repo token 到本地 remote，沙箱内 `push/pull` 无需代理接触 token。自定义工具：MCP + OAuth token 保险柜，Claude 通过专用代理调用，Harness 对凭证无感知。

### Session 不是上下文窗口

长时间任务常超出上下文窗口，传统手段（compaction、trimming）涉及不可逆的保留/丢弃决策。Managed Agents 中，Session 作为**上下文窗口外部的持久上下文对象**——`getEvents()` 可按位置切片回溯，支持从断点恢复、回退重读。事件转换（context engineering）由 Harness 自由编码，Session 仅保证持久性和可查询性。

### 多脑多手

**Many Brains：** 解耦后 Harness 变为无状态，容器按需供给（`execute` 调用时才创建），推理可不等容器。p50 TTFT 下降约 60%，p95 下降超 90%。扩展多脑只需启动更多无状态 Harness。

**Many Hands：** 每个 Hand 是 `execute(name, input) → string` 的统一接口——可以是容器、手机、Pokémon 模拟器。Harness 不知道也不关心。Brain 之间可传递 Hand。

## 要点

- **Pets vs Cattle**：有状态、需人工护理的 Pet 模式不适合可扩展代理系统；Harness 和容器都应是无状态、可互换的 Cattle
- **接口稳定性 > 实现细节**：`execute()`, `wake()`, `getSession()`, `emitEvent()` 等通用接口使实现可替换，类似 OS 的 `read()` 系统调用
- **安全结构性修复**：凭证不应与不可信代码共存于同一环境；token 注入和 vault 代理是两种互补模式
- **上下文窗口 ≠ 会话**：Session 作为外部上下文对象，避免不可逆的 compaction/trimming 决策，支持灵活回溯
- **TTFT 即用户体验**：启动时不阻塞等待沙箱，推理优先，TTFT 显著下降
- **Meta-Harness 定位**：Managed Agents 是一种元 Harness，对具体 Harness 不做假设，可容纳 Claude Code、领域专用 Harness 等多种形态

## 关联

- [[building-effective-agents]] — 同系列前作，构建有效代理的原则
- [[context-engineering]] — 上下文工程，compaction/trimming 等技术
- [[claude-code-harness]] — Claude Code 作为 Harness 的实现

## 来源

- 作者：Lance Martin, Gabe Cemaj, Michael Cohen
- 机构：Anthropic
- 原文链接：https://www.anthropic.com/engineering/managed-agents
- 原始文件：0003-inbox/Scaling Managed Agents Decoupling the brain from the hands.md
