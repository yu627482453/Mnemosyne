---
title: "CNN"
topic: "3001-深度学习"
layer: L2
kind: standard
tags: [深度学习, 计算机视觉, AI, CNN]
aliases: [cnn, 卷积神经网络, convolutional-neural-network]
created: 2026-05-20
updated: 2026-05-20
source: manual
status: draft
summary: "卷积神经网络，利用卷积核提取层次化特征的深度学习架构，是计算机视觉的基础模型"
---

# CNN

## 核心内容

卷积神经网络（CNN）是深度学习在计算机视觉领域的奠基性架构。由 Yann LeCun 等人 1998 年在 LeNet-5 中首次系统化提出，2012 年 AlexNet 在 ImageNet 上大获成功后成为计算机视觉的主流方法。

CNN 利用可学习的卷积核在输入上滑动提取局部特征，通过参数共享机制大幅减少参数量，配合池化层逐步降低空间维度，最终通过全连接层输出分类或回归结果。

## 要点

- 卷积层：使用可学习卷积核提取局部特征，参数共享减少参数量
- 池化层：下采样降低特征图尺寸，提供平移不变性；常见最大池化和平均池化
- 层次化特征提取：浅层提取边缘/纹理，深层提取语义/物体
- 激活函数 ReLU：解决 sigmoid/tanh 的梯度消失问题
- 主要应用：图像分类、目标检测（R-CNN/YOLO）、图像分割（FCN/U-Net）、人脸识别

## 关联

- [[resnet]] — 引入残差连接的深层卷积网络
- [[transformer]] — 基于自注意力的序列建模架构，ViT 将其引入视觉
- [[alexnet]] — 2012 年 ImageNet 冠军，CNN 复兴标志

## 来源

- LeCun et al., "Gradient-Based Learning Applied to Document Recognition", IEEE 1998
- Krizhevsky et al., "ImageNet Classification with Deep CNNs", NeurIPS 2012
- 手动整理
