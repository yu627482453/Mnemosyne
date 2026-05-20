---
title: "Transformer"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [深度学习, NLP, 注意力机制, LLM, AI]
aliases: [transformer, 变换器, 自注意力架构]
created: 2026-05-20
updated: 2026-05-20
source: manual
status: draft
summary: "基于自注意力机制的序列建模架构，2017年由Google提出，是当前LLM的基础架构"
---

# Transformer

## 核心内容

Transformer 是由 Google 在 2017 年论文《Attention Is All You Need》中提出的深度学习架构。核心创新是完全基于注意力机制，摒弃了传统的循环神经网络（RNN）和卷积神经网络（CNN）结构，实现了高效的并行计算和长距离依赖建模。

Transformer 的提出直接催生了后续的 BERT、GPT 系列以及当前的大语言模型（LLM），是当前 AI 领域最重要的基础架构之一。

## 要点

- 自注意力机制（Self-Attention）：计算序列中每个元素与其他所有元素的关联权重，解决长距离依赖
- 多头注意力（Multi-Head Attention）：并行运行多组注意力，捕获不同类型的关联模式
- 位置编码（Positional Encoding）：弥补注意力机制无法感知序列顺序的缺陷
- 前馈网络（Feed-Forward Network）：每个位置独立应用的全连接层
- 残差连接与层归一化：稳定深层网络训练，缓解梯度消失

## 关联

- [[self-attention]] — 自注意力机制详解
- [[multi-head-attention]] — 多头注意力机制
- [[positional-encoding]] — 位置编码方法
- [[BERT]] — 基于 Transformer 编码器的预训练模型
- [[GPT]] — 基于 Transformer 解码器的生成式模型

## 来源

- 论文：Vaswani et al., "Attention Is All You Need", NeurIPS 2017
- 手动整理
