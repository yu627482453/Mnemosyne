---
title: "Claude Code Auto Mode"
topic: "3002-LLM"
layer: L2
kind: standard
tags: [AI, 机器学习, LLM]
aliases: [claude-code-auto-mode, Claude Code 自动模式, auto mode]
created: 2026-05-21
updated: 2026-05-21
source: url
source_url: "https://www.anthropic.com/engineering/claude-code-auto-mode"
status: draft
summary: "用分类器减少权限弹窗并保留安全边界的自动模式"
---

# Claude Code Auto Mode

## 核心内容

Claude Code Auto Mode 试图在"频繁权限确认"和"完全跳过权限"之间提供更安全的折中方案。它通过输入层的提示注入探测与输出层的转录分类器，自动判断一部分原本需要人工确认的操作，以降低 approval fatigue，同时维持安全边界。

## 要点

- 输入层会扫描工具输出，识别潜在 prompt injection 并附加警告。
- 输出层使用两阶段 transcript classifier，对 shell、外部工具、越界文件操作等行为做执行前判定。
- 文章给出的实验结果显示：在真实流量上 FPR 为 0.4%，在 synthetic exfiltration 上 FNR 为 0%。

## 关联

- [[claude-code-auto-mode]] — 概念加工页
- [[claude-code]] — 实体：Claude Code（Anthropic CLI 工具）
- [[sandbox-vs-skip-permissions-vs-auto-mode]] — 三种权限模式对比

## 来源

- https://www.anthropic.com/engineering/claude-code-auto-mode
