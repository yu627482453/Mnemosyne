---
title: "Session Log vs Context Window"
layer: L3
kind: comparison
comparison_axis: "Architecture"
lhs: "Session Log（事件日志）"
rhs: "Context Window（上下文窗口）"
updated: 2026-05-22
source: ["3000-Agent/scaling-managed-agents.md"]
tags: [AI, context-engineering, session-management, architecture, comparison]
status: draft
summary: >
  对比 Session Log 与 Context Window 两种上下文管理策略。Context Window 受 token 限制，
  超出时需不可逆的 compaction/trimming 决策；Session Log 作为外部持久对象，通过
  getEvents() 按位置切片检索，支持回溯、重读和断点恢复。Context Window 优势在于即时
  可用、无需外部查询；Session Log 优势在于不丢失信息、支持灵活回溯。Managed Agents
  选择 Session Log 作为持久层，上下文工程由 Harness 自由编码。
---

# Session Log vs Context Window

## 对比概览

| 维度 | Session Log | Context Window |
|------|-------------|----------------|
| 持久性 | 持久化，外部存储 | 瞬态，受 token 限制 |
| 回溯能力 | getEvents() 任意切片 | 仅窗口内可用 |
| 容量 | 无上限 | token 硬限制 |
| 恢复能力 | wake() 断点恢复 | 超出窗口即丢失 |
| 管理复杂度 | 需上下文工程 | 即时可用 |

## 适用场景
- **选 Session Log**：长时间任务，需断点恢复、灵活回溯
- **选 Context Window**：短任务，上下文确定性高、无需外部存储

## 依据
- [[scaling-managed-agents]]（L2）
