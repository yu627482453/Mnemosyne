---
title: "Session Log vs Context Window"
layer: L3
kind: comparison
comparison_axis: context-management
lhs: Session Log（事件日志）
rhs: Context Window（上下文窗口）
updated: 2026-05-22
source:
  - "3000-Agent/scaling-managed-agents.md"
tags:
  - context-engineering
  - session-management
  - LLM
  - AI
  - agent-architecture
summary: >
  Session Log 是 agent 平台层面的持久化事件存储，Context Window 是 LLM 推理时的内存工作区。
  前者是 append-only、完全可逆的外部存储；后者受 token 限制、内容经不可逆裁剪/compaction 后
  可能永久丢失。Managed Agents 的架构将两者分离：session log 保证完整性和可恢复性，harness
  负责决定将哪些上下文切片加载到 context window 中。
---

## 对比

| 维度 | Session Log | Context Window |
|------|-------------|----------------|
| **存储位置** | Agent 平台（外部持久化） | LLM 推理内存 |
| **容量限制** | 无理论上限（持久化存储） | 模型 token limit（如 200K） |
| **写入方式** | Append-only（harness emitEvent） | 每次推理调用传入 |
| **内容修改** | 不可变（事件一经写入不可删除） | 可被 compaction/trimming 修改 |
| **可逆性** | 完全可逆——任意历史事件可回溯 | 不可逆——裁剪后内容永久丢失 |
| **查询方式** | `getEvents()` 按位置切片 | 全量传入（受 token 限制） |
| **生命周期** | 跨 session 持久化 | 单次推理，随 context 窗口滑动而淘汰 |

## 关系

```
Session Log --(harness 切片/转换)--> Context Window --> Claude 推理
     ^                                                  |
     +------- emitEvent (追加新事件) ------------------+
```

Session Log 是 ground truth——完整的、不可变的事件记录。Context Window 是工作视图——harness 从 session log 中选择和变换后传入的上下文子集。这种分离意味着：

1. **错误的上下文工程决策可恢复**：即使 harness 裁剪了重要内容，原始事件仍在 session log 中
2. **harness 策略可独立演进**：上下文裁剪/组织策略随模型能力变化，session log 不受影响
3. **支持跨 session 学习**：新 harness 可以通过 `getSession(id)` 读取完整历史

## 来源

- [[scaling-managed-agents]]
- <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
