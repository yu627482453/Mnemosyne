---
title: "Session as Context Object"
layer: L3
kind: concept
processing_path: "3000-Agent → 0102-wiki-concepts/agent/session-as-context-object"
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
  Session as Context Object 是将 agent 会话的完整事件日志作为 LLM 上下文窗口外部的持久化存储对象的
  设计模式。与 compaction/summarization 等不可逆压缩不同，session log 保留完整事件流，通过
  getEvents() 接口按位置切片检索，支持回溯、重读和任意转换。上下文管理（裁剪、组织、缓存优化）
  由 harness 负责，session 只保证持久化和可查询性。
---

## 定义

Session as Context Object 是 Managed Agents 中的上下文管理策略：将 agent session 的完整事件日志持久化存储在 Claude 的上下文窗口*之外*，作为可被随时查询的上下文对象。Claude 通过 harness 调用 `getEvents()` 按位置切片检索事件流，而非直接拥有整个上下文。

## 与传统方法的区别

| 方法 | 机制 | 可逆性 | 风险 |
|------|------|--------|------|
| Compaction | Claude 生成上下文摘要，丢弃原始消息 | 不可逆 | 可能丢弃未来轮次需要的 token |
| Context Trimming | 选择性删除旧 tool result / thinking block | 不可逆 | 裁剪标准可能与未来需求不匹配 |
| Memory Tool | Claude 写入文件，跨 session 学习 | 部分可逆 | 依赖 Claude 主动写入 |
| **Session as Context Object** | 完整事件日志，按需切片检索 | 完全可逆 | 需要持久化存储 + 检索接口 |

## 工作方式

1. harness 通过 `emitEvent(id, event)` 向 session log 追加事件
2. session log 是 append-only 的持久化存储
3. 需要上下文时，harness 通过 `getEvents()` 按位置切片获取事件
4. 获取的事件可在 harness 中做任意转换（裁剪、重排、缓存对齐）后再传入 Claude 的 context window
5. Claude 可以回溯到特定时刻之前的事件，重读关键操作的前导上下文

## 关注点分离

- **Session**：只保证持久化和可查询——不关心具体哪些上下文被保留
- **Harness**：负责上下文工程（裁剪策略、prompt cache 优化、格式化）——可随模型能力演进而独立更新

## 来源

- [[scaling-managed-agents]]
- <https://arxiv.org/pdf/2512.24601> — 上下文作为 REPL 外部对象的先前探索
- <https://www.anthropic.com/engineering/managed-agents>
