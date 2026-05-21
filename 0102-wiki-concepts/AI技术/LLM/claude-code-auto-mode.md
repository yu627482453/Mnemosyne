---
title: "Claude Code Auto Mode"
layer: L3
kind: concept
processing_path: "AI技术/LLM"
updated: 2026-05-21
source: [3002-LLM/claude-code-auto-mode.md]
tags: [AI, 机器学习, LLM]
status: draft
summary: "一种在保留安全边界前提下自动通过部分权限请求的代理模式"
---

# Claude Code Auto Mode

## 定义

Claude Code Auto Mode 是一种用于减少权限确认频率、同时维持安全边界的代理执行模式。

## 解释

它在输入侧对工具返回内容做 prompt injection 探测，在输出侧对 agent transcript 做分级判定。系统将不同动作分层处理：安全白名单工具、项目内文件操作，以及需要 classifier 介入的更高风险动作。其目标不是彻底取消权限机制，而是在保留控制边界的前提下自动通过一部分高概率会被用户批准的请求。

## 关键引用

- [[claude-code-auto-mode]] — 用分类器减少权限弹窗并保留安全边界的自动模式

## 相关概念

- [[prompt-injection]]
- [[agent-safety]]
- [[permission-model]]

## 争议与分歧

<!-- 当前仅单一来源，暂无冲突信息 -->
