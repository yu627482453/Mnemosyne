---
title: "Transformer"
layer: L3
kind: concept
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source_topics: [3001-深度学习]
---

# Transformer

## 定义

基于自注意力机制的序列建模架构，2017 年由 Google 在《Attention Is All You Need》中提出。核心创新是完全基于注意力机制，摒弃了传统的 RNN 和 CNN 结构，实现了高效的并行计算和长距离依赖建模。

## 核心机制

- **自注意力（Self-Attention）**：计算序列中每个元素与其他所有元素的关联权重，直接捕获全局依赖
- **多头注意力（Multi-Head Attention）**：并行运行多组注意力，每组关注不同的表示子空间，捕获不同类型的关联模式
- **位置编码（Positional Encoding）**：通过正弦/余弦函数为序列注入位置信息，弥补注意力机制对顺序不敏感的缺陷
- **前馈网络（Feed-Forward Network）**：每个位置独立应用的两层全连接网络，增加非线性变换能力
- **残差连接与层归一化**：围绕每个子层添加残差连接后接层归一化，稳定深层网络训练

## 关键来源

- [[transformer]]（L2）— 原始标准化知识条目
- Vaswani et al., "Attention Is All You Need", NeurIPS 2017

## 相关概念

- [[self-attention]] — 自注意力机制
- [[BERT]] — 基于 Transformer 编码器的预训练模型
- [[GPT]] — 基于 Transformer 解码器的生成式模型
