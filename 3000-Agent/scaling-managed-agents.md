---
id: f44cb74c
title: "Scaling Managed Agents: Decoupling the brain from the hands"
topic: agent
layer: L2
kind: standard
tags:
  - AI
  - LLM
  - agent-architecture
  - context-engineering
  - infrastructure
  - sandbox
  - managed-agents
  - session-management
aliases:
  - Managed Agents 架构
  - Brain-Hands Decoupling
created: 2026-05-22
updated: 2026-05-22
source: "https://www.anthropic.com/engineering/managed-agents"
source_url: "https://www.anthropic.com/engineering/managed-agents"
resource_refs:
  - "0001-resource/agent/scaling-managed-agents/20260522-1.png"
  - "0001-resource/agent/scaling-managed-agents/20260522-2.png"
  - "0001-resource/agent/scaling-managed-agents/20260522-3.png"
  - "0001-resource/agent/scaling-managed-agents/20260522-4.png"
content_hash: 54d6496c
status: published
summary: >
  Anthropic 工程博客介绍 Managed Agents 的架构设计理念——将 agent 系统的"大脑"（harness/推理循环）
  与"双手"（sandbox/工具执行环境）解耦。核心思路借鉴操作系统的虚拟化抽象：通过稳定接口（session、
  harness、sandbox）替代单体耦合设计，使各组件可独立替换和扩缩容。文章阐述了四个关键主题：(1) 从
  pets 到 cattle 的基础设施演进——harness 和容器都可无状态重启；(2) 安全边界重构——auth token 永
  不暴露在 sandbox 内；(3) session 作为 context window 之外的持久化上下文对象；(4) 多 brain 多
  hand 的横向扩展能力。解耦后 p50 TTFT 下降约 60%，p95 下降超 90%。整体定位为"元 harness"——
  对具体 harness 实现不做假设，只定义通用接口，以适应未来模型能力的演进。
---

## 核心内容

Anthropic 推出 Managed Agents——Claude Platform 上托管的长时域 agent 运行服务。其架构核心是将 agent 拆分为三个可独立演进的接口：**Session**（不可变的事件日志）、**Harness**（调用 Claude 并路由 tool call 的循环）、**Sandbox**（Claude 可运行代码和编辑文件的执行环境）。这种设计使每个组件可以独立替换，不互相耦合。

## 文章要点

1. **从 pets 到 cattle**：早期单体容器设计导致容器故障即会话丢失。解耦后 harness 和容器都变成无状态——harness 崩溃后可借助 session log 恢复，容器挂了可重建。
2. **安全边界**：auth token 永远不进入 sandbox。Git 克隆在 sandbox 初始化时完成，MCP 工具通过代理调用外部服务，token 存储在 sandbox 之外的 vault 中。
3. **Session 不是 context window**：session 是 context window 外部的持久化存储对象。harness 通过 `getEvents()` 按位置切片检索事件流，支持回溯、重读和任意转换。
4. **多 brain 多 hand**：`execute(name, input) → string` 接口统一了所有工具。brain 按需 provisioning 容器，brain 之间可以传递 hand。TTFT 中位数下降约 60%，p95 下降超 90%。
5. **元 harness**：Managed Agents 不做任何关于具体 harness 实现的假设——可以运行 Claude Code 也可以运行领域专用的 agent harness。

---

## 原文主体

*使用 Claude Managed Agents 请参阅[官方文档](https://platform.claude.com/docs/en/managed-agents/overview)。*

工程博客上持续讨论的主题是如何[构建有效的 agent](https://www.anthropic.com/engineering/building-effective-agents)、为[长时运行任务](https://www.anthropic.com/engineering/harness-design-long-running-apps)设计 [harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。贯穿这些工作的共同线索是：harness 编码了对 Claude 无法独立完成之事的假设。但这些假设需要被不断审视，因为随着模型能力的提升，它们会[过时](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)。

举一个例子：在之前的工作中，[我们发现](https://www.anthropic.com/engineering/harness-design-long-running-apps) Claude Sonnet 4.5 会在感知到上下文窗口接近上限时过早结束任务——这种行为有时被称为"上下文焦虑"。我们通过在 harness 中添加上下文重置来解决这个问题。但当我们在 Claude Opus 4.5 上使用相同的 harness 时，发现这种行为已经消失了。那些重置操作变成了无用功。

我们预计 harness 会持续演进。因此我们构建了 Managed Agents：一个在 Claude Platform 中托管运行长时域 agent 的服务，通过一小组旨在比任何特定实现（包括我们今天使用的实现）更持久存续的接口来运行。

构建 Managed Agents 意味着解决一个计算机科学中的古老问题：如何为"[尚不存在的程序](http://www.catb.org/esr/writings/taoup/html/ch03s01.html)"设计系统。几十年前，操作系统通过将硬件虚拟化为抽象——*进程、文件*——来解决这个问题，这些抽象足够通用，可以服务于那些当时还不存在的程序。这些抽象存续得比硬件更久。`read()` 命令不在意它访问的是 1970 年代的磁盘组还是现代 SSD。上层抽象保持稳定，而下层实现可以自由变更。

Managed Agents 遵循了相同的模式。我们将 agent 的组件虚拟化：session（所有事件的只追加日志）、harness（调用 Claude 并将 Claude 的 tool call 路由到相关基础设施的循环）和 sandbox（Claude 可以运行代码和编辑文件的执行环境）。这使得每个组件的实现都可以被替换，而不会干扰其他组件。我们对这些接口的形状有明确的意见，但对接口背后运行的具体实现不作假设。

![架构图](0001-resource/agent/scaling-managed-agents/20260522-1.png)

### 不要养宠物

我们最初将所有 agent 组件放在单个容器中，这意味着 session、agent harness 和 sandbox 共享同一个环境。这种方法有好处，包括文件编辑是直接系统调用，而且没有需要设计的服务边界。

但通过将所有内容耦合到一个容器中，我们遇到了一个古老的运维问题：我们养了一只[*宠物*](https://cloudscaling.com/blog/cloud-computing/the-history-of-pets-vs-cattle/)。在 pets-vs-cattle 的类比中，宠物是有名字、需要人工照料、你无法承受丢失的个体，而 cattle 是可互换的。在我们的情况下，服务器变成了宠物；如果容器故障，session 就丢失了。如果容器无响应，我们必须设法让它恢复健康。

照料容器意味着调试无响应的卡住 session。我们唯一的窗口是 WebSocket 事件流，但这不能告诉我们*哪里*出了问题，这意味着 harness 中的 bug、事件流中的数据包丢失或容器离线都呈现相同的症状。为了弄清楚出了什么问题，工程师必须在容器内打开 shell，但由于容器通常也持有用户数据，这种方法本质上意味着我们缺乏调试能力。

第二个问题是，harness 假设 Claude 工作的内容就在它所处的容器中。当客户要求我们将 Claude 连接到他们的 VPC 时，他们要么必须将其网络与我们的网络对等互联，要么必须在自己的环境中运行我们的 harness。当需要将 harness 连接到不同基础设施时，内置于 harness 中的假设就变成了问题。

### 将大脑与双手解耦

我们最终采用的方案是，将我们称为"大脑"（Claude 及其 harness）的部分与"双手"（执行操作的 sandbox 和工具）以及"session"（session 事件日志）解耦。每个部分变成了对其他部分几乎不作假设的接口，每个部分都可以独立故障或被替换。

**harness 离开容器。** 将大脑与双手解耦意味着 harness 不再驻留在容器内部。它调用容器就像调用任何其他工具一样：`execute(name, input) → string`。容器变成了 cattle。如果容器宕机，harness 将该故障捕获为 tool-call 错误并传回给 Claude。如果 Claude 决定重试，可以通过标准配方 `provision({resources})` 重新初始化一个新容器。我们不再需要照料故障容器恢复健康。

**从 harness 故障中恢复。** harness 本身也变成了 cattle。因为 session 日志位于 harness 之外，harness 中没有任何东西需要在崩溃后存活。当 harness 发生故障时，可以通过 `wake(sessionId)` 启动一个新的，使用 `getSession(id)` 获取事件日志，并从最后一个事件恢复。在 agent 循环期间，harness 通过 `emitEvent(id, event)` 向 session 写入事件，以保持事件的持久化记录。

![解耦架构图](0001-resource/agent/scaling-managed-agents/20260522-2.png)

**安全边界。** 在耦合设计中，Claude 生成的任何不受信任的代码都在与凭据相同的容器中运行——因此 prompt injection 只需说服 Claude 读取自己的环境变量。一旦攻击者获得了这些 token，他们就可以生成新的、不受限制的 session 并将工作委托给它们。缩小权限范围是一个明显的缓解措施，但这编码了一个关于 Claude 在受限 token 下不能做什么的假设——而 Claude 正变得越来越聪明。结构性的修复方案是确保 token 永远不会从 Claude 生成代码运行的 sandbox 中可达。

我们使用了两种模式来确保这一点。认证信息可以与资源绑定，也可以保存在 sandbox 之外的 vault 中。对于 Git，我们在 sandbox 初始化期间使用每个仓库的访问 token 克隆仓库，并将其配置到本地 git remote 中。Git 的 `push` 和 `pull` 操作在 sandbox 内工作，而 agent 永远不会直接处理 token。对于自定义工具，我们支持 MCP 并将 OAuth token 存储在安全 vault 中。Claude 通过专用代理调用 MCP 工具；该代理接受与 session 关联的 token，从 vault 获取相应的凭据，然后调用外部服务。harness 永远不会接触到任何凭据。

### Session 不是 Claude 的 context window

长时域任务通常超出 Claude 上下文窗口的长度，而处理这一问题的标准方法都涉及关于保留什么的不可逆决策。我们在[之前的工作](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)中探讨了这些上下文工程技术。例如，compaction 让 Claude 保存其上下文窗口的摘要，memory tool 让 Claude 将上下文写入文件，从而实现跨 session 学习。这可以与上下文裁剪配合使用，后者选择性地移除 token，例如旧的工具结果或 thinking block。

但不可逆的选择性保留或丢弃上下文的决策可能导致失败。很难知道未来轮次需要哪些 token。如果消息被 compaction 步骤转换，harness 会将 compact 后的消息从 Claude 的上下文窗口移除，而这些消息只有在被存储的情况下才能恢复。之前的工作[探索了](https://arxiv.org/pdf/2512.24601)通过将上下文存储为存在于上下文窗口*之外*的对象来解决这个问题。例如，上下文可以是 REPL 中的一个对象，LLM 通过编写代码来过滤或切片它以程序化方式访问。

![Session 上下文图](0001-resource/agent/scaling-managed-agents/20260522-3.png)

在 Managed Agents 中，session 提供了相同的好处——作为存在于 Claude 上下文窗口之外的上下文对象。但与在 sandbox 或 REPL 中存储不同，上下文被持久化存储在 session 日志中。接口 `getEvents()` 允许大脑通过选择事件流的位置切片来查询上下文。该接口可以灵活使用，允许大脑从上次停止读取的地方继续，回退到特定时刻之前的几个事件来查看前导事件，或重读特定操作之前的上下文。

获取到的任何事件也可以在进入 Claude 上下文窗口之前在 harness 中进行转换。这些转换可以是 harness 编码的任何内容，包括为实现高 prompt cache 命中率而进行的上下文组织以及上下文工程。我们将 session 中可恢复的上下文存储与 harness 中任意的上下文管理的关注点分离，因为我们无法预测未来的模型需要什么样的具体上下文工程。接口将上下文管理推入 harness，只保证 session 是持久��可供查询的。

### 多脑，多手

**多脑。** 将大脑与双手解耦解决了我们最早遇到的客户投诉之一。当团队希望 Claude 对其自有 VPC 中的资源进行操作时，唯一的途径是将其网络与我们的网络对等互联，因为持有 harness 的容器假定每个资源都在它旁边。一旦 harness 不再在容器中，这个假设就消失了。同样的变化也带来了性能收益。当我们最初将大脑放在容器中时，意味着多个大脑需要相应数量的容器。对于每个大脑，在容器被 provisioning 之前不能进行推理；每个 session 都要承担完整的容器启动成本。每个 session，即使是那些永远不会用到 sandbox 的，都必须克隆仓库、启动进程、从服务器获取待处理事件。

这段等待时间体现在 time-to-first-token (TTFT) 上——它衡量一个 session 在接受工作和产生第一个响应 token 之间的时间。TTFT 是用户*感受*最敏锐的延迟。

将大脑与双手解耦意味着容器仅在被需要时才由大脑通过 tool call (`execute(name, input) → string`) provisioning。因此，不需要容器立即可用的 session 就不必等待容器。一旦编排层从 session 日志中拉取了待处理事件，推理就可以开始。使用这种架构，我们的 p50 TTFT 下降了约 60%，p95 下降了超过 90%。扩展到多个大脑只需要启动许多无状态 harness，并在需要时将它们连接到双手。

**多手。** 我们还希望每个大脑能够连接到多只手。在实践中，这意味着 Claude 必须对多个执行环境进行推理，并决定将工作发送到哪里——这比在单一 shell 中操作更难。我们从大脑在单个容器中开始，因为早期的模型不具备这种能力。随着智能的发展，单个容器反而成了限制：当容器故障时，大脑触及的每只手的状��都会丢失。

将大脑与双手解耦使每只手成为一个工具，`execute(name, input) → string`：传入名称和输入，返回一个字符串。这个接口支持任何自定义工具、任何 MCP 服务器以及我们的自有工具。harness 不知道 sandbox 是容器、手机还是 Pokémon 模拟器。而且因为没有手耦合到任何大脑，大脑可以将手传递给其他大脑。

![多脑多手图](0001-resource/agent/scaling-managed-agents/20260522-4.png)

### 结论

我们面临的挑战是一个古老的挑战：如何为"尚不存在的程序"设计系统。操作系统通过将硬件虚拟化为足够通用的抽象，存续了几十年，服务于那些当时还不存在的程序。在 Managed Agents 中，我们的目标是设计一个能够容纳未来围绕 Claude 的各种 harness、sandbox 或其他组件的系统。

Managed Agents 是一个秉承同样精神的元 harness——不对 Claude 未来需要的*特定* harness 持有立场。相反，它是一个具有通用接口的系统，允许许多不同的 harness。例如，Claude Code 是一个出色的 harness，我们在各种任务中广泛使用。我们也展示了任务特定的 agent harness 在狭窄领域中表现出色。Managed Agents 可以容纳任何这些，随着时间推移匹配 Claude 的智能水平。

元 harness 设计意味着对围绕 Claude 的接口有明确的意见：我们预计 Claude 需要操作状态（session）和执行计算（sandbox）的能力。我们也预计 Claude 需要能够扩展到多个大脑和多只手。我们设计的接口使这些能够在长时间内可靠、安全地运行。但我们对 Claude 将需要的大脑或手的数量或位置不作任何假设。

### 致谢

作者：Lance Martin、Gabe Cemaj 和 Michael Cohen。感谢 Nodir Turakulov 和 Jeremy Fox 关于这些主题的有益对话。特别感谢 Agents API 团队和 Jake Eaton 的贡献。

---

> 来源: [Scaling Managed Agents: Decoupling the brain from the hands — Anthropic Engineering Blog](https://www.anthropic.com/engineering/managed-agents)
