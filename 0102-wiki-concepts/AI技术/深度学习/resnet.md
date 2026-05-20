---
title: "ResNet"
layer: L3
kind: concept
processing_path: "AI技术/深度学习"
updated: 2026-05-20
source_topics: [3001-深度学习]
---

# ResNet

## 定义

残差网络（Residual Network），通过残差连接（Skip Connection）使输入绕过中间层直连到输出，将学习目标从完整映射 H(x) 转为残差 F(x)=H(x)-x，解决了深层网络的退化问题。

## 核心机制

- **残差连接**：标准网络学习 H(x)，残差网络学习 F(x)=H(x)-x，输出为 F(x)+x。当恒等映射最优时，网络只需将 F(x) 推至零，比学习恒等映射容易得多
- **批归一化（Batch Normalization）**：在每个卷积层后、激活函数前对 mini-batch 做归一化，加速训练收敛、允许更大学习率、提供轻微正则化效果
- **瓶颈结构（Bottleneck）**：先用 1×1 卷积降维（如 256→64），再 3×3 卷积，最后 1×1 恢复维度（64→256），大幅减少深层网络的计算量

## 关键来源

- [[resnet]]（L2）— 残差网络标准化知识条目
- He et al., "Deep Residual Learning for Image Recognition", CVPR 2016

## 相关概念

- [[cnn]] — 卷积神经网络基础架构
- [[transformer]] — Transformer 同样采用残差连接
- [[densenet]] — 密集连接，残差思想的进一步延伸
