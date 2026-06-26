---
title: "Contextual Retrieval：上下文检索技术"
topic: "3001-RAG与检索"
layer: L2
id: "52bc9c18"
kind: standard
tags: [rag, contextual-retrieval, embedding, bm25, reranking, vector-search, knowledge-base, llm-application]
aliases: [上下文检索, Contextual Embeddings, Contextual BM25]
created: "2026-06-26"
updated: "2026-06-26"
source: "url"
source_url: "https://www.anthropic.com/engineering/contextual-retrieval"
resource_refs:
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-1.png
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-2.png
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-3.png
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-4.png
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-5.png
  - 0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-6.png
planned_links: [tf-idf, semantic-similarity, vector-database, knowledge-base, context-window, chunk]
status: draft
summary: "Anthropic 提出的 Contextual Retrieval（上下文检索）方法，通过在文档分块前为每个 chunk 添加上下文解释（Contextual Embeddings + Contextual BM25），解决传统 RAG 因切块导致的上下文丢失问题。实验表明该方法可将检索失败率降低 49%，结合 reranking 后降低 67%。核心技术是使用 Claude 为每个 chunk 生成简洁的上下文说明（50-100 tokens），然后进行 embedding 和 BM25 索引。配合 prompt caching 技术，处理成本仅为每百万文档 tokens 1.02 美元。文章详细对比了不同 embedding 模型（Gemini、Voyage）、检索策略（top-5/10/20）和 reranking 方案的性能表现，为构建高质量 RAG 系统提供了实践指南。"
content_hash: "16598726"
---

# Contextual Retrieval：上下文检索技术

## 核心提炼

传统 RAG 系统在文档分块时会破坏上下文完整性，导致检索失败。例如某个 chunk 写着"公司营收增长 3%"，但不知道是哪家公司、哪个季度，这使得精确检索变得困难。

Anthropic 提出的 **Contextual Retrieval** 解决方案的核心创新是：**在 embedding 和建立 BM25 索引之前，为每个 chunk 预置上下文说明**。具体做法是用 Claude 读取完整文档，为每个 chunk 生成一段简洁的情境化描述（50-100 tokens），说明该 chunk 在整体文档中的位置和背景。

技术组合效果：
- **Contextual Embeddings**：为每个 chunk 添加上下文后再 embedding，降低检索失败率 35%
- **Contextual BM25**：为每个 chunk 添加上下文后再建立 BM25 索引
- **两者结合**：降低检索失败率 49%（从 5.7% → 2.9%）
- **+ Reranking**：进一步降低至 67%（从 5.7% → 1.9%）

成本控制：利用 **prompt caching** 技术，上下文生成的一次性成本仅为每百万文档 tokens $1.02，因为完整文档只需加载到缓存一次，后续处理每个 chunk 时都可复用缓存内容。

这个方法的关键价值在于：它不改变检索架构，只是预处理阶段的增强，对现有 RAG 系统侵入性小，但效果提升显著。

## 关键概念

- [[rag]] — 检索增强生成
- [[embedding]] — 向量嵌入
- [[bm25]] — 词频匹配算法
- [[reranking]] — 二次排序
- [[prompt-caching]] — Claude 提示词缓存
- [[vector-database]] — 向量数据库
- [[semantic-similarity]] — 语义相似度
- [[tf-idf]] — 词频-逆文档频率
- [[chunk]] — 文档分块
- [[knowledge-base]] — 知识库
- [[context-window]] — 上下文窗口

## 原文要点

### 1. 问题背景
- 小知识库（< 200k tokens）可直接放入 prompt，配合 prompt caching 实现低成本高效访问
- 大知识库需要 RAG，但传统 RAG 的文档分块会破坏上下文

### 2. 传统 RAG 流程
- 预处理：文档切块 → embedding → 存入向量库
- 运行时：用户查询 → 语义检索 + BM25 精确匹配 → 组合去重 → 取 top-K 添加到 prompt

### 3. Contextual Retrieval 方法
- 预处理增强：文档切块 → **为每个 chunk 生成上下文** → embedding + BM25 索引
- Prompt 示例：给 Claude 完整文档和单个 chunk，让它生成一段简洁的情境化说明
- 成本：利用 prompt caching，$1.02/M document tokens（一次性）

### 4. 实验结果
- 测试数据：代码库、小说、ArXiv 论文、科学论文
- 最佳配置：Gemini Text 004 或 Voyage embedding + top-20 chunks
- 性能提升：
  - Contextual Embeddings：失败率 ↓35%（5.7% → 3.7%）
  - Contextual Embeddings + BM25：失败率 ↓49%（5.7% → 2.9%）
  - + Reranking（Cohere）：失败率 ↓67%（5.7% → 1.9%）

### 5. 实施建议
- Chunk 边界和大小会影响检索性能
- Gemini 和 Voyage embedding 表现最佳
- 可自定义 contextualizer prompt 适配特定领域
- Top-20 chunks 比 top-5/10 效果更好
- Reranking 会增加延迟和成本，需要权衡

### 6. 关键结论
- Embeddings + BM25 优于单独使用 embeddings
- 为 chunks 添加上下文显著提升检索准确率
- 所有优化手段可叠加使用，达到最佳性能

## 来源

- 作者：Daniel Ford
- 机构：Anthropic
- 原文链接：https://www.anthropic.com/engineering/contextual-retrieval
- 发布日期：2024 年

---
## 原文笔记

### 引言

要使 AI 模型在特定场景下发挥作用，它通常需要访问背景知识。例如，客户支持聊天机器人需要了解其服务的特定业务知识，法律分析机器人需要了解大量过往案例。

开发者通常使用检索增强生成（RAG）来增强 AI 模型的知识。RAG 是一种从知识库中检索相关信息并将其附加到用户提示词的方法，可以显著增强模型的响应能力。问题在于，传统 RAG 解决方案在编码信息时会移除上下文，这通常导致系统无法从知识库中检索到相关信息。

在本文中，我们概述了一种显著改进 RAG 检索步骤的方法。该方法称为"上下文检索"（Contextual Retrieval），使用两种子技术：上下文嵌入（Contextual Embeddings）和上下文 BM25（Contextual BM25）。该方法可以将检索失败次数减少 49%，当与重排序（reranking）结合使用时，可减少 67%。这些代表了检索准确性的重大改进，直接转化为下游任务的更好性能。

您可以使用 Claude 轻松部署自己的上下文检索解决方案，参考我们的 [cookbook](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide)。

### 关于简单使用更长提示词的说明

有时最简单的解决方案是最好的。如果您的知识库小于 200,000 个 tokens（大约 500 页材料），您可以将整个知识库包含在给模型的提示词中，无需 RAG 或类似方法。

几周前，我们为 Claude 发布了 [提示词缓存](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)，这使得这种方法显著更快且更具成本效益。开发者现在可以在 API 调用之间缓存常用提示词，将延迟降低 > 2倍，成本降低高达 90%（您可以通过阅读我们的 [提示词缓存 cookbook](https://platform.claude.com/cookbook/misc-prompt-caching) 来了解其工作原理）。

然而，随着知识库的增长，您需要一个更可扩展的解决方案。这就是上下文检索的用武之地。

### RAG 入门：扩展到更大的知识库

对于不适合上下文窗口的较大知识库，RAG 是典型解决方案。RAG 通过以下步骤预处理知识库：

1. 将知识库（文档的"语料库"）分解为较小的文本块，通常不超过几百个 tokens；
2. 使用嵌入模型将这些块转换为编码含义的向量嵌入；
3. 将这些嵌入存储在向量数据库中，该数据库允许按语义相似性进行搜索。

在运行时，当用户向模型输入查询时，向量数据库用于根据与查询的语义相似性找到最相关的块。然后，将最相关的块添加到发送给生成模型的提示词中。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-1.png]]

虽然嵌入模型擅长捕获语义关系，但它们可能会错过关键的精确匹配。幸运的是，有一种较旧的技术可以在这些情况下提供帮助。BM25（Best Matching 25）是一种排名函数，它使用词汇匹配来查找精确的单词或短语匹配。它对于包含唯一标识符或技术术语的查询特别有效。

BM25 基于 TF-IDF（词频-逆文档频率）概念构建。TF-IDF 衡量一个词对文档集合中的文档的重要性。BM25 通过考虑文档长度并对词频应用饱和函数来改进这一点，这有助于防止常见词主导结果。

以下是 BM25 在语义嵌入失败的情况下如何成功的示例：假设用户在技术支持数据库中查询"错误代码 TS-999"。嵌入模型可能会找到关于一般错误代码的内容，但可能会错过精确的"TS-999"匹配。BM25 会查找这个特定的文本字符串以识别相关文档。

RAG 解决方案可以通过以下步骤结合使用嵌入和 BM25 技术来更准确地检索最适用的块：

1. 将知识库（文档的"语料库"）分解为较小的文本块，通常不超过几百个 tokens；
2. 为这些块创建 TF-IDF 编码和语义嵌入；
3. 使用 BM25 根据精确匹配找到顶部块；
4. 使用嵌入根据语义相似性找到顶部块；
5. 使用排名融合技术组合和去重来自 (3) 和 (4) 的结果；
6. 将 top-K 个块添加到提示词中以生成响应。

通过同时利用 BM25 和嵌入模型，传统 RAG 系统可以提供更全面和准确的结果，平衡精确的词项匹配和更广泛的语义理解。

这种方法允许您以成本效益的方式扩展到巨大的知识库，远远超出单个提示词所能容纳的范围。但这些传统的 RAG 系统有一个重大限制：它们经常破坏上下文。

### 传统 RAG 中的上下文难题

在传统 RAG 中，文档通常被分割成较小的块以实现高效检索。虽然这种方法对许多应用程序都很有效，但当单个块缺乏足够的上下文时，可能会导致问题。

例如，想象您在知识库中嵌入了一组财务信息（比如美国 SEC 文件），并且您收到以下问题：*"ACME Corp 在 2023 年第二季度的营收增长是多少？"*

相关块可能包含文本：*"公司的营收比上一季度增长了 3%。"* 然而，这个块本身并没有指明它指的是哪家公司或相关的时间段，这使得检索正确信息或有效使用信息变得困难。

### 引入上下文检索

上下文检索通过在嵌入（"上下文嵌入"）和创建 BM25 索引（"上下文 BM25"）之前，为每个块预置特定于块的解释性上下文来解决这个问题。

让我们回到我们的 SEC 文件集合示例。以下是如何转换块的示例：

```
original_chunk = "公司的营收比上一季度增长了 3%。"

contextualized_chunk = "这个块来自 ACME 公司 2023 年第二季度业绩的 SEC 文件；上一季度的营收为 3.14 亿美元。公司的营收比上一季度增长了 3%。"
```

值得注意的是，过去已经提出了使用上下文改进检索的其他方法。其他提案包括：[向块添加通用文档摘要](https://aclanthology.org/W02-0405.pdf)（我们进行了实验，但收效甚微）、[假设文档嵌入](https://arxiv.org/abs/2212.10496)和[基于摘要的索引](https://www.llamaindex.ai/blog/a-new-document-summary-index-for-llm-powered-qa-systems-9a32ece2f9ec)（我们评估了但性能较低）。这些方法与本文提出的方法不同。

### 实施上下文检索

当然，手动注释知识库中的数千甚至数百万个块将是一项艰巨的工作。为了实施上下文检索，我们求助于 Claude。我们编写了一个提示词，指示模型使用整体文档的上下文提供简洁的、特定于块的上下文来解释块。我们使用以下 Claude 3 Haiku 提示词为每个块生成上下文：

```
<document> 
{{WHOLE_DOCUMENT}} 
</document> 
这是我们想要在整个文档中定位的块
<chunk> 
{{CHUNK_CONTENT}} 
</chunk> 
请给出一个简短简洁的上下文，以便将这个块定位在整个文档中，目的是改进块的搜索检索。只回答简洁的上下文，不要其他内容。
```

生成的上下文文本，通常为 50-100 个 tokens，在嵌入之前和创建 BM25 索引之前被预置到块中。

以下是预处理流程在实践中的样子：

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-2.png]]

如果您有兴趣使用上下文检索，可以从我们的 [cookbook](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide) 开始。

### 使用提示词缓存降低上下文检索的成本

上下文检索在 Claude 中以低成本实现，这要归功于我们上面提到的特殊提示词缓存功能。使用提示词缓存，您不需要为每个块传递参考文档。您只需将文档加载到缓存中一次，然后引用先前缓存的内容。假设 800 token 块、8k token 文档、50 token 上下文指令和每个块 100 tokens 的上下文，**生成上下文化块的一次性成本为每百万文档 tokens 1.02 美元**。

### 方法论

我们在各种知识领域（代码库、小说、ArXiv 论文、科学论文）、嵌入模型、检索策略和评估指标上进行了实验。我们在[附录 II](https://assets.anthropic.com/m/1632cded0a125333/original/Contextual-Retrieval-Appendix-2.pdf) 中包含了我们用于每个领域的一些问题和答案示例。

下图显示了使用表现最佳的嵌入配置（Gemini Text 004）并检索 top-20 块时所有知识领域的平均性能。我们使用 1 减去 recall@20 作为评估指标，该指标衡量在 top-20 块中未能检索到的相关文档的百分比。您可以在附录中看到完整结果 - 上下文化在我们评估的每个嵌入-源组合中都提高了性能。

### 性能改进

我们的实验表明：

- **上下文嵌入将 top-20 块检索失败率降低了 35%**（5.7% → 3.7%）。
- **结合上下文嵌入和上下文 BM25 将 top-20 块检索失败率降低了 49%**（5.7% → 2.9%）。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-3.png]]

### 实施注意事项

在实施上下文检索时，需要牢记几个注意事项：

1. **块边界**：考虑如何将文档分割成块。块大小、块边界和块重叠的选择会影响检索性能。
2. **嵌入模型**：尽管上下文检索在我们测试的所有嵌入模型中都提高了性能，但某些模型可能比其他模型受益更多。我们发现 [Gemini](https://ai.google.dev/gemini-api/docs/embeddings) 和 [Voyage](https://www.voyageai.com/) 嵌入特别有效。
3. **自定义上下文化器提示词**：虽然我们提供的通用提示词效果很好，但您可能能够通过针对您的特定领域或用例定制的提示词获得更好的结果（例如，包含可能仅在知识库中其他文档中定义的关键术语词汇表）。
4. **块数量**：在上下文窗口中添加更多块会增加包含相关信息的机会。然而，更多信息可能会分散模型的注意力，因此这是有限度的。我们尝试了传递 5、10 和 20 个块，发现使用 20 个在这些选项中表现最佳（见附录进行比较），但值得在您的用例上进行实验。

**始终运行评估**：通过向响应生成传递上下文化的块并区分什么是上下文、什么是块，可能会改进响应生成。

### 通过重排序进一步提升性能

在最后一步中，我们可以将上下文检索与另一种技术结合起来，以获得更多的性能改进。在传统 RAG 中，AI 系统搜索其知识库以查找潜在相关的信息块。对于大型知识库，这种初始检索通常会返回大量块（有时数百个），相关性和重要性各不相同。

重排序是一种常用的过滤技术，以确保只有最相关的块传递给模型。重排序提供更好的响应并降低成本和延迟，因为模型处理的信息更少。关键步骤是：

1. 执行初始检索以获取 top 潜在相关的块（我们使用了 top 150）；
2. 将 top-N 块以及用户的查询传递给重排序模型；
3. 使用重排序模型，根据其与提示词的相关性和重要性为每个块打分，然后选择 top-K 块（我们使用了 top 20）；
4. 将 top-K 块作为上下文传递给模型以生成最终结果。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-4.png]]

### 性能改进

市场上有几种重排序模型。我们使用 [Cohere reranker](https://cohere.com/rerank) 进行了测试。Voyage [也提供了一个 reranker](https://docs.voyageai.com/docs/reranker)，尽管我们没有时间测试它。我们的实验表明，在各个领域中，添加重排序步骤可以进一步优化检索。

具体来说，我们发现重排序的上下文嵌入和上下文 BM25 将 top-20 块检索失败率降低了 67%（5.7% → 1.9%）。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-5.png]]

### 成本和延迟考虑

重排序的一个重要考虑因素是对延迟和成本的影响，尤其是在重排序大量块时。因为重排序在运行时添加了一个额外的步骤，所以它不可避免地增加了少量延迟，即使重排器并行对所有块进行评分。在为更好的性能重排序更多块与为更低的延迟和成本重排序更少块之间存在固有的权衡。我们建议在您的特定用例上尝试不同的设置以找到合适的平衡。

### 结论

我们进行了大量测试，比较了上述所有技术的不同组合（嵌入模型、BM25 的使用、上下文检索的使用、重排器的使用以及检索的 top-K 结果总数），所有这些都跨越了各种不同的数据集类型。以下是我们发现的摘要：

1. Embeddings+BM25 优于单独的 embeddings；
2. Voyage 和 Gemini 拥有我们测试的最佳嵌入；
3. 将 top-20 块传递给模型比仅 top-10 或 top-5 更有效；
4. 为块添加上下文大大提高了检索准确性；
5. 重排序优于不重排序；
6. **所有这些好处都是可叠加的**：为了最大化性能改进，我们可以将上下文嵌入（来自 Voyage 或 Gemini）与上下文 BM25 结合使用，再加上重排序步骤，并将 20 个块添加到提示词中。

我们鼓励所有使用知识库的开发者使用[我们的 cookbook](https://platform.claude.com/cookbook/capabilities-contextual-embeddings-guide) 来实验这些方法，以释放新的性能水平。

### 附录 I

以下是 Retrievals @ 20 的跨数据集、嵌入提供商、除嵌入外使用 BM25、使用上下文检索和使用重排序的结果细分。

有关 Retrievals @ 10 和 @ 5 的细分以及每个数据集的示例问题和答案，请参见[附录 II](https://assets.anthropic.com/m/1632cded0a125333/original/Contextual-Retrieval-Appendix-2.pdf)。

![[0001-resource/3001-RAG与检索/contextual-retrieval-20260626075635-6.png]]

跨数据集和嵌入提供商的 1 减 recall @ 20 结果。

### 致谢

研究和写作由 Daniel Ford 完成。感谢 Orowa Sikder、Gautam Mittal 和 Kenneth Lien 提供的关键反馈，Samuel Flamini 实施了 cookbook，Lauren Polansky 负责项目协调，Alex Albert、Susan Payne、Stuart Ritchie 和 Brad Abrams 帮助塑造了这篇博客文章。
