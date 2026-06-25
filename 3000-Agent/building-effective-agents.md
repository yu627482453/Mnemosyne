---
title: "构建高效的 AI Agent"
topic: "3000-Agent"
layer: L2
id: "36636a47"
content_hash: "26d011dd"
kind: standard
tags:
  - agent-architecture
  - workflow-patterns
  - prompt-chaining
  - routing
  - parallelization
  - orchestrator-workers
  - evaluator-optimizer
  - tool-engineering
  - augmented-llm
aliases:
  - "Building Effective Agents"
  - "高效Agent构建"
created: 2026-06-03
updated: 2026-06-25
source: url
source_url: "https://www.anthropic.com/engineering/building-effective-agents"
planned_links:
  - model-context-protocol
resource_refs:
  - "0001-resource/3000-Agent/building-effective-agents/augmented-llm-20260625170209.png"
  - "0001-resource/3000-Agent/building-effective-agents/prompt-chaining-20260625170209.png"
  - "0001-resource/3000-Agent/building-effective-agents/routing-20260625170210.png"
  - "0001-resource/3000-Agent/building-effective-agents/parallelization-20260625170210.png"
  - "0001-resource/3000-Agent/building-effective-agents/orchestrator-workers-20260625170211.png"
  - "0001-resource/3000-Agent/building-effective-agents/evaluator-optimizer-20260625170211.png"
  - "0001-resource/3000-Agent/building-effective-agents/autonomous-agent-20260625170211.png"
  - "0001-resource/3000-Agent/building-effective-agents/coding-agent-flow-20260625170212.png"
status: draft
summary: "Anthropic 基于与数十个团队合作一年的实践经验，系统阐述了构建 LLM Agent 的方法论。核心论点：最成功的 Agent 实现并非依赖复杂框架，而是使用简单、可组合的模式。文章首先区分了 workflow（预定义路径编排）和 agent（动态决策）两类 agentic 系统，提出从最简方案出发、仅在必要时增加复杂度的原则。以 augmented LLM 为基础构建块，逐层递进介绍五种 workflow 模式（prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer）和自主 agent，每种模式都给出了适用场景和生产案例。附录深入讨论了 customer support 和 coding agent 两大实践领域，以及 tool prompt engineering 的方法论，提出 ACI（Agent-Computer Interface）应与 HCI 同等重视。三大核心原则：保持简单、优先透明、精心设计工具接口。"
---

## 核心提炼

Anthropic 从与数十个团队的合作中提炼出一条核心经验：**成功的 Agent 实现不靠复杂框架，而靠简单、可组合的模式**。文章构建了一个从简到繁的架构谱系——augmented LLM 是原子构建块，五种 workflow 模式（prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer）提供确定性的编排方案，而自主 agent 则在开放任务中释放模型的决策能力。关键洞察是：workflow 和 agent 不是替代关系而是互补关系，选择标准在于任务的确定性和灵活性。文章特别强调 tool 的设计应与 prompt 同等重视，提出 ACI（Agent-Computer Interface）概念，将 HCI 的设计思维迁移到 agent 工具接口上。在 SWE-bench 实践中，工具优化时间远超 prompt 优化时间，这一反直觉发现极具指导意义。

## 关键概念

- [[prompt-chaining]]
- [[routing]]
- [[parallelization]]
- [[orchestrator-workers]]
- [[evaluator-optimizer]]
- [[augmented-llm]]
- [[tool-engineering]]
- [[model-context-protocol]]
- [[agent-vs-workflow]]

## 原文要点

1. **Agent 定义与分类** — 区分 workflow（预定义路径）和 agent（动态决策），统称 agentic systems
2. **复杂度最小化原则** — 从最简方案开始，仅在有明确收益时才增加复杂度；单次 LLM 调用 + RAG 对许多应用已足够
3. **框架使用的审慎态度** — 框架降低入门门槛但引入抽象层，容易掩盖底层 prompt/response 导致调试困难；建议先直接用 LLM API
4. **Augmented LLM 构建块** — LLM + retrieval + tools + memory，模型能主动生成搜索查询、选择工具、决定保留什么信息
5. **Prompt Chaining** — 任务分解为序列步骤，前一步输出作为后一步输入，可在中间插入 gate 检查；适用于可清晰分解的固定子任务
6. **Routing** — 分类输入并导向专门处理流程；适用于有明确类别且各类别需不同处理的复杂任务
7. **Parallelization** — sectioning（独立子任务并行）和 voting（同一任务多次运行取共识）两个变体；适用于可并行加速或需要多视角的任务
8. **Orchestrator-Workers** — 中心 LLM 动态分解任务、委派给 worker、综合结果；与 parallelization 的区别在于子任务不预定义，由 orchestrator 动态决定
9. **Evaluator-Optimizer** — 一个 LLM 生成响应，另一个评估并反馈，循环迭代；适用于有明确评估标准且迭代改进有明确价值的场景
10. **自主 Agent** — 以工具调用循环为核心，从环境获取 ground truth 评估进展；适用于步骤数不可预测的开放任务，但需要 sandbox 测试和 guardrails
11. **工具 Prompt Engineering（ACI）** — 工具定义应获得与 prompt 同等的 attention；关键建议：给模型足够 token "思考"、格式贴近自然文本、消除格式 overhead、poka-yoke 防错设计
12. **三大核心原则** — 保持 agent 设计简单、显式展示规划步骤（透明性）、精心设计工具文档和测试

## 来源

- 作者：Erik S.、Barry Zhang（Anthropic）
- 机构：Anthropic
- 原文链接：https://www.anthropic.com/engineering/building-effective-agents
- 原始文件：`0003-inbox/Building Effective AI Agents.md`

---

## 原文笔记

### 引言

过去一年，Anthropic 与数十个团队合作，在各行各业构建大语言模型（LLM）Agent。始终如一地，最成功的实现并没有使用复杂的框架或专用库，而是用简单、可组合的模式来构建。

### 什么是 Agent

"Agent" 可以有多种定义。一些客户将 agent 定义为完全自主的系统，能独立运行较长时间，使用各种工具完成复杂任务。另一些人用这个术语描述更具规范性的实现，遵循预定义的工作流。Anthropic 将所有这些变体归类为 **agentic systems（智能体系统）**，但做了一个重要的架构区分：**workflows（工作流）** 和 **agents（智能体）**：

- **Workflows** 是 LLM 和工具通过预定义代码路径进行编排的系统
- **Agents** 是 LLM 动态指导自身流程和工具使用的系统，保持对任务完成方式的控制权

### 何时（以及何时不）使用 Agent

使用 LLM 构建应用时，建议找到尽可能简单的解决方案，仅在必要时增加复杂度。这可能意味着完全不需要构建 agentic 系统。Agentic 系统通常以更高的延迟和成本换取更好的任务表现，需要考虑这种权衡何时合理。

当需要更多复杂度时，workflow 为定义明确的任务提供可预测性和一致性，而 agent 在需要灵活性和模型驱动决策的场景中是更好的选择。然而对于许多应用，通过检索和上下文示例优化单次 LLM 调用通常就足够了。

### 何时以及如何使用框架

有许多框架可以简化 agentic 系统的实现，包括 Claude Agent SDK、AWS Strands Agents SDK、Rivet（拖拽式 GUI 工作流构建器）和 Vellum。这些框架通过简化标准低级任务（调用 LLM、定义和解析工具、链式调用）使入门变得容易。然而它们经常创建额外的抽象层，可能掩盖底层的 prompt 和 response，使调试更加困难。它们还可能诱使开发者在简单设置就足够时增加不必要的复杂度。

建议开发者从直接使用 LLM API 开始：许多模式只需几行代码就能实现。如果确实使用框架，要确保理解底层代码。对底层机制的错误假设是客户错误的常见来源。

### 构建块、Workflow 和 Agent

#### 构建块：Augmented LLM（增强型 LLM）

Agentic 系统的基本构建块是通过增强能力（如检索、工具和记忆）提升的 LLM。当前模型可以主动使用这些能力——生成自己的搜索查询、选择合适的工具、决定保留什么信息。

建议关注两个关键实现方面：将这些能力针对特定用例进行定制，确保它们为 LLM 提供简单、文档完善的接口。实现这些增强的一种方法是通过 Model Context Protocol（MCP），允许开发者通过简单的客户端实现与不断增长的第三方工具生态集成。

![[augmented-llm-20260625170209.png]]

#### Workflow：Prompt Chaining（提示链）

Prompt chaining 将任务分解为一系列步骤，每个 LLM 调用处理前一步的输出。可以在任何中间步骤添加程序化检查（gate），确保流程仍在正轨上。

![[prompt-chaining-20260625170209.png]]

**适用场景：** 适用于任务可以清晰分解为固定子任务的情况。主要目标是用延迟换取更高准确度，使每次 LLM 调用处理更简单的任务。

**实用示例：**
- 先生成营销文案，然后翻译成另一种语言
- 先写文档大纲，检查大纲是否满足特定标准，然后基于大纲撰写文档

#### Workflow：Routing（路由）

Routing 对输入进行分类并将其导向专门的后续任务。这种 workflow 允许关注点分离，构建更专业化的 prompt。没有这种 workflow，针对一种输入类型的优化可能损害其他输入的表现。

![[routing-20260625170210.png]]

**适用场景：** 适用于有明确类别、各类别需分别处理的复杂任务，且分类能被 LLM 或传统分类模型/算法准确处理。

**实用示例：**
- 将不同类型的客服查询（一般问题、退款请求、技术支持）导向不同的下游流程、prompt 和工具
- 将简单/常见问题路由到更小巧、成本高效的模型（如 Claude Haiku 4.5），将困难/罕见问题路由到更强大的模型（如 Claude Sonnet 4.5）

#### Workflow：Parallelization（并行化）

LLM 有时可以同时处理一个任务，并通过程序化方式聚合输出。Parallelization 有两个关键变体：**Sectioning（分段）**——将任务分解为独立子任务并行运行；**Voting（投票）**——多次运行同一任务以获得多样化输出。

![[parallelization-20260625170210.png]]

**适用场景：** 当子任务可以并行以提速，或需要多视角/多次尝试以获得更高可信度结果时有效。对于有多个考量的复杂任务，当每个考量由单独的 LLM 调用处理时，LLM 通常表现更好。

**实用示例：**
- **Sectioning**：实现 guardrails，一个模型实例处理用户查询，另一个筛查不当内容或请求；自动化评估中每个 LLM 调用评估模型表现的不同方面
- **Voting**：多个不同 prompt 审查代码漏洞；多个 prompt 评估内容是否不当，用不同投票阈值平衡误报和漏报

#### Workflow：Orchestrator-Workers（编排者-工人）

中心 LLM 动态分解任务，委派给 worker LLM，并综合它们的结果。

![[orchestrator-workers-20260625170211.png]]

**适用场景：** 适用于无法预测所需子任务的复杂任务（例如在编码中，需要更改的文件数量和每个文件中的变更性质都取决于具体任务）。与 parallelization 的拓扑相似，但关键区别在于灵活性——子任务不是预定义的，而是由 orchestrator 根据具体输入动态决定的。

**实用示例：**
- 每次对多个文件进行复杂更改的编码产品
- 涉及从多个来源收集和分析可能相关信息的搜索任务

#### Workflow：Evaluator-Optimizer（评估者-优化者）

一个 LLM 调用生成响应，另一个提供评估和反馈，形成循环。

![[evaluator-optimizer-20260625170211.png]]

**适用场景：** 当有明确的评估标准，且迭代改进能提供可衡量的价值时特别有效。两个良好适配的标志：第一，当人类明确表达反馈时 LLM 响应能明显改进；第二，LLM 能提供这样的反馈。这类似于人类作家撰写精修文档时经历的迭代写作过程。

**实用示例：**
- 文学翻译中翻译 LLM 可能初次无法捕捉细微差别，但评估 LLM 能提供有用的批评
- 需要多轮搜索和分析来收集全面信息的复杂搜索任务，评估者决定是否需要进一步搜索

#### Agent（自主智能体）

随着 LLM 在关键能力上的成熟——理解复杂输入、进行推理和规划、可靠使用工具、从错误中恢复——Agent 正在生产中崭露头角。Agent 以人类用户的命令或互动讨论开始工作。一旦任务明确，Agent 独立规划和操作，可能在需要时返回人类获取更多信息或判断。在执行过程中，Agent 在每一步从环境获取"ground truth"（如工具调用结果或代码执行）以评估进展至关重要。Agent 可以在检查点或遇到阻碍时暂停等待人类反馈。任务通常在完成时终止，但也常包含停止条件（如最大迭代次数）以保持控制。

Agent 能处理复杂任务，但实现往往很简单。它们通常只是在循环中基于环境反馈使用工具的 LLM。因此，精心设计工具集及其文档至关重要。

![[autonomous-agent-20260625170211.png]]

**适用场景：** 适用于开放性问题，其中无法预测所需步骤数，也无法硬编码固定路径。LLM 可能运行多个回合，需要对其决策能力有一定信任。Agent 的自主性使其成为在可信环境中扩展任务的理想选择。但自主性意味着更高成本和错误复合的可能性，建议在沙盒环境中进行广泛测试并配备适当的 guardrails。

**实用示例：**
- 解决 SWE-bench 任务的编码 Agent，涉及基于任务描述编辑多个文件
- "Computer use" 参考实现，Claude 使用计算机完成任务

![[coding-agent-flow-20260625170212.png]]

### 组合和定制这些模式

这些构建块不是规范性的。它们是开发者可以根据不同用例塑造和组合的常见模式。成功的关键（与任何 LLM 功能一样）是衡量表现并迭代实现。**仅当复杂度的增加能可证明地改善结果时才考虑增加复杂度。**

### 总结

LLM 领域的成功不在于构建最复杂的系统，而在于为你的需求构建**正确的**系统。从简单提示开始，通过全面评估进行优化，仅在简单方案不足时才添加多步 agentic 系统。

实现 Agent 时遵循三个核心原则：
1. 保持 agent 设计的**简单性**
2. 通过显式展示 agent 的规划步骤来优先保证**透明性**
3. 通过全面的工具**文档和测试**精心打造 agent-计算机接口（ACI）

框架可以帮助快速起步，但在转向生产时不要犹豫减少抽象层、用基础组件构建。遵循这些原则，可以创建不仅强大而且可靠、可维护、受用户信任的 agent。

### 附录 1：Agent 实践

#### A. 客户支持

客户支持将熟悉的聊天机器人界面与通过工具集成增强的能力结合在一起。这对更开放的 agent 是天然适配，因为：支持交互自然遵循对话流程同时需要访问外部信息和行动；可以集成工具来拉取客户数据、订单历史和知识库文章；退款或更新工单等操作可以程序化处理；成功可以通过用户定义的解决方案清晰衡量。一些公司已通过基于使用的定价模式（仅为成功解决收费）证明了这种方法的可行性。

#### B. 编码 Agent

软件开发领域展示了 LLM 功能的巨大潜力，能力已从代码补全演进到自主问题解决。Agent 特别有效因为：代码解决方案可通过自动化测试验证；Agent 可以使用测试结果作为反馈迭代解决方案；问题空间是明确定义和结构化的；输出质量可以客观衡量。Anthropic 自己的实现中，Agent 现在可以仅基于 pull request 描述解决 SWE-bench Verified 基准中的真实 GitHub issue。但虽然自动化测试有助于验证功能，人类审查对确保解决方案与更广泛的系统需求保持一致仍然至关重要。

### 附录 2：工具的 Prompt Engineering

无论构建哪种 agentic 系统，工具都可能是 agent 的重要组成部分。工具使 Claude 能够通过指定确切的结构和定义来与外部服务和 API 交互。工具定义和规范应该获得与整体 prompt 同等的 prompt engineering 关注。

通常有多种方式来规范同一操作。例如，可以通过写 diff 或重写整个文件来指定文件编辑。对于结构化输出，可以在 markdown 或 JSON 中返回代码。在软件工程中，这些差异是表面性的，可以无损转换。但某些格式对 LLM 来说比其他格式更难编写。写 diff 需要在写新代码之前知道 chunk header 中有多少行在变化。在 JSON 中写代码（相比 markdown）需要额外转义换行符和引号。

关于工具格式选择的建议：
- 给模型足够的 token 在"陷入死角"之前"思考"
- 保持格式接近模型在训练数据中自然出现的格式
- 确保没有格式"开销"，如需要准确计数数千行代码或转义所写的任何代码

一个经验法则是考虑在人机界面（HCI）上投入了多少精力，并计划在创建好的**agent-计算机界面（ACI）**上投入同等的精力。建议：
- 站在模型的角度思考：基于描述和参数，是否显而易见如何使用这个工具？好的工具定义通常包括示例用法、边界情况、输入格式要求以及与其他工具的清晰边界
- 考虑如何更改参数名称或描述使事情更直观，就像为团队中的初级开发者写一份优秀的文档字符串
- 测试模型如何使用你的工具：在工作台中运行大量示例输入，查看模型犯什么错误，然后迭代
- 对工具进行 Poka-yoke（防错设计），改变参数使错误更难发生

在构建 SWE-bench agent 时，Anthropic 实际花在优化工具上的时间比整体 prompt 更多。例如，发现模型在使用相对文件路径的工具时会在 agent 离开根目录后犯错。为了修复这个问题，将工具改为始终要求绝对文件路径——发现模型完美地使用了这种方法。
