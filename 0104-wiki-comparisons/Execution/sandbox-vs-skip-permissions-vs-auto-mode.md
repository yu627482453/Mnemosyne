---
title: "sandbox vs skip-permissions vs auto-mode"
layer: L3
kind: comparison
comparison_axis: "Execution"
lhs: "sandbox"
rhs: "skip-permissions"
updated: 2026-05-21
source: [3002-LLM/claude-code-auto-mode.md]
tags: [AI, 机器学习, LLM, security, permission-model]
status: draft
summary: "比较 sandbox、完全跳过权限与 auto mode 三种权限执行策略。sandbox 安全性最高但维护成本大；skip-permissions 交互最少但几乎无保护；auto-mode 通过分类器决策在安全与效率间取平衡。适用于需要根据风险等级和运维投入选择权限模型的工程场景。"
---

# sandbox vs skip-permissions vs auto-mode

## 对比概览

| 维度 | sandbox | skip-permissions | auto-mode |
|------|----------|-----------|-----------|
| 安全性 | 高 | 低 | 中高 |
| 维护成本 | 高 | 低 | 中 |
| 用户交互负担 | 中 | 低 | 低 |
| 权限控制方式 | 环境隔离 | 全部放开 | 分类器决策 |

## 适用场景

- **选 sandbox**：需要强隔离、愿意承担额外配置与维护成本
- **选 skip-permissions**：追求最少交互、接受几乎无保护的风险
- **选 auto-mode**：希望减少审批疲劳，同时保留部分安全边界

## 依据

- [[claude-code-auto-mode]] — 用分类器减少权限弹窗并保留安全边界的自动模式
