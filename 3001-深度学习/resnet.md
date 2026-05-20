---
title: "ResNet"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [深度学习, 计算机视觉, AI, CNN, 残差网络]
aliases: [resnet, 残差网络, residual-network]
created: 2026-05-20
updated: 2026-05-20
source: manual
status: draft
summary: "引入残差连接解决深层网络退化问题，使训练100+层网络成为可能，2015年由何凯明提出"
---

# ResNet

## 核心内容

ResNet（残差网络）由何凯明等人在 2015 年提出，解决了深层网络训练中的退化问题——网络越深训练误差反而升高。核心创新是残差连接（Skip Connection），将输入直接加到输出上：H(x) = F(x) + x，网络学习残差 F(x) = H(x) - x 而非直接学习目标映射。

残差连接的思想被广泛采用，Transformer、DenseNet 等都受其启发，证明了"深度"本身的价值。

## 要点

- 残差连接（Skip Connection）：输入直连到输出，网络学习残差而非完整映射
- 恒等映射保障：即使新增层不学任何东西（F(x)=0），网络至少保持原有性能
- 使训练 100+ 层深层网络成为可能，ResNet-152 在 ImageNet 上表现优异
- 批归一化（Batch Normalization）：加速训练、稳定梯度
- 瓶颈结构（Bottleneck）：1×1 卷积降维再升维，减少计算量

## 关联

- [[cnn]] — 卷积神经网络基础架构
- [[transformer]] — Transformer 也采用了残差连接
- [[densenet]] — 密集连接网络，残差思想的延伸

## 来源

- He et al., "Deep Residual Learning for Image Recognition", CVPR 2016
- 手动整理
