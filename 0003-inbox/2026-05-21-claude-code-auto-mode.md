---
title: "Claude Code Auto Mode 学习摘记"
date: 2026-05-21
source: url
source_url: "https://www.anthropic.com/engineering/claude-code-auto-mode"
status: raw
---

# Claude Code Auto Mode 学习摘记

## 原始内容

# Claude Code auto mode: a safer way to skip permissions

Published Mar 25, 2026

Claude Code users approve 93% of permission prompts. We built classifiers to automate some decisions, increasing safety while reducing approval fatigue.

By default, Claude Code asks users for approval before running commands or modifying files. This keeps users safe, but it also means a lot of clicking "approve." Over time that leads to approval fatigue.

Users have two solutions: a built-in sandbox where tools are isolated, or the `--dangerously-skip-permissions` flag that disables all permission prompts. Sandboxing is safe but high-maintenance; bypassing permissions is zero-maintenance but offers no protection. Manual prompts sit in the middle, and users accept 93% of them anyway.

## How it works

Auto mode uses two layers of defense: one for what Claude reads, one for what Claude does.

At the input layer, a prompt-injection probe scans tool outputs before they enter the agent's context. When content looks like an attempt to hijack behavior, the probe adds a warning.

At the output layer, the transcript classifier evaluates each action against decision criteria before execution. The classifier runs in two stages: a fast single-token filter, followed by chain-of-thought reasoning only if the first filter flags the transcript.

## Threat model

An agent might take a dangerous action for four reasons:

1. **Overeager behavior** - genuinely trying to help but takes initiative beyond what the user would approve
2. **Honest mistakes** - misunderstands the blast radius
3. **Prompt injection** - instructions planted in a file or webpage hijack the agent
4. **A misaligned model** - pursues a goal of its own (not currently seen in practice)

Examples from internal incident logs include: scope escalation (batch deleting branches from vague requests), credential exploration, agent-inferred parameters, sharing via external service, and safety-check bypass.

## How permission decisions work

**Tier 1**: Built-in safe-tool allowlist and user settings for read-only tools.

**Tier 2**: In-project file operations allowed without classifier calls.

**Tier 3**: Transcript classifier sees everything else - shell commands, web fetches, external tools, subagent spawns, filesystem operations outside project directory.

## The classifier decision criteria

The classifier's prompt has a fixed template with three customizable slots.

**Fixed template**: Evaluation rules determine real-world impact. User intent rules establish authorization boundaries.

**Customizable slots**: The "environment" defines trust boundaries. Block rules cover: destroy/exfiltrate, degrade security posture, cross trust boundaries, and bypass review. Allow exceptions handle benign technical matches.

## Results

Evaluated on three datasets:
- Real internal traffic (n=10,000)
- Real overeager actions (n=52)
- Synthetic data exfiltration (n=1,000)

Full pipeline results: 0.4% FPR on real traffic, 17% FNR on overeager actions, 0% FNR on synthetic exfiltration.

## 来源信息

- 来源：url
- URL：https://www.anthropic.com/engineering/claude-code-auto-mode
- 采集日期：2026-05-21

## 处理状态

- [x] 已完成 Claude 处理
- [ ] 待移入回收站
