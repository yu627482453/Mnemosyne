# skill-ingest：知识摄入（L1 → L2 → L3）

> 执行要求：开始前先用 TaskCreate 创建包含全部步骤(1-11)的 tasklist，每完成一步标记 completed。


> 触发：用户 `@` 引用 inbox 文件要求处理

## 前置检查

1. 确认目标文件在 `0003-inbox/` 下且存在
2. 读取全文，提取标题、来源、核心内容
3. 扫描原文中的图片引用

## L2 拆分判断

> 不拆 inbox 文件，在创建 L2 时按知识概念逻辑拆分。

**拆分条件**（满足任一即建议拆分为多个 L2）：
- 包含 3+ 个独立知识概念（有独立标题且概念间可独立成文）
- 跨 2+ 个 topic 域（如同时涉及 Agent + LLM基础）
- 原文超过 10000 字且各节概念不重叠

**不拆分**：内容紧密关联拆开后上下文断裂、用户要求合并。

**拆分粒度**：
- 每个 L2 对应一个独立知识主题
- 多个 L2 共享同一 `source_url`，各自 `source` 指向同一 inbox 文件
- slug 命名：`{原slug}-{概念slug}`（如 `hello-agents-ch1-agent-loop`）

**必须先输出 L2 拆分计划表，等用户确认后才能创建 L2 文件：**

| # | L2 slug | 来源章节 | 推荐 topic | 概念摘要 |
|---|---------|---------|-----------|---------|
| 1 | hello-agents-ch1-what-is-agent | §1.1 什么是智能体 | 3000-Agent | 智能体定义四要素 |
| 2 | hello-agents-ch1-agent-mechanism | §1.2 构成与运行原理 | 3000-Agent | PEAS 模型、Agent Loop |
| 3 | hello-agents-ch1-build-first-agent | §1.3 动手体验 | 3000-Agent | 实践案例 |

**用户确认操作：**
- **确认全部**：按计划创建 L2
- **改名**：调整 L2 slug
- **合并**：把 2+ 个 L2 合为一个
- **再拆**：某个 L2 仍太大，继续拆
- **调整 topic**：改推荐归属
- **删除**：某个章节不需要 ingest
- **不拆**：整个文件作为单个 L2

**未获用户确认前，禁止创建任何 L2 文件。**

## 执行步骤

### 1. 判断归属主题目录

- 对照 `0100-wiki-meta/configs/topics.yaml`
- 推荐时同时给中英文选项（如 `AI技术/Agent`）
- **首次归档须用户确认**；边界主题/多主题交叉必须询问
- 无匹配：按 topics.yaml 规则创建，格式 `{4位编号}-{显示名}`

### 2. 生成 slug 与文件名
> 模型：此步骤可用 Haiku。

命名规则（D018）：空格→`-`，主体`.`→`_`，仅最后一个`.`是扩展名。
英文优先，3-5 推荐选项，`rg --files` 查重，重名追加 `-2`/`-3`。
slug 仅用于路径，不替代标题。

### 3. 处理图片资源

1. 扫描 L1 中的图片 URL
2. 逐张下载到 `0001-resource/{topic}/{slug}/{timestamp}.{ext}`
   - `{topic}` 必须是完整的主题目录名（如 `3000-Agent`），不是缩写或 slug
3. **下载失败→暂停通知用户**，等待手动处理后继续
4. 正文远程引用改写为 `![[0001-resource/...]]`
5. 写入 `resource_refs`，与正文 1:1 对齐
6. 无图片则 `resource_refs: []`

### 4. 生成 id 与 content_hash

```bash
# id: SHA256(topic+slug+created)[:8]
python3 -c "import hashlib,json; s=json.dumps({'topic':'{topic}','slug':'{slug}','created':'{created}'},sort_keys=True); print(hashlib.sha256(s.encode()).hexdigest()[:8])" || python -c "import hashlib,json; s=json.dumps({'topic':'{topic}','slug':'{slug}','created':'{created}'},sort_keys=True); print(hashlib.sha256(s.encode()).hexdigest()[:8])"

# content_hash: 仅对正文部分（frontmatter 之后的内容）SHA256[:8]
python3 -c "
import hashlib,re
with open('{path}','r') as f: c=f.read()
body=re.split(r'^---\s*$',c,maxsplit=2,flags=re.MULTILINE)[2] if c.startswith('---') else c
print(hashlib.sha256(body.encode()).hexdigest()[:8])
" || python -c "
import hashlib,re
with open('{path}','r') as f: c=f.read()
body=re.split(r'^---\s*$',c,maxsplit=2,flags=re.MULTILINE)[2] if c.startswith('---') else c
print(hashlib.sha256(body.encode()).hexdigest()[:8])
"
```

### 5. 创建 L2

> 翻译：原文中译使用 Haiku 模型，分段 prompt "翻译为中文，保留技术术语和段落结构"。

按 `t-knowledge.md` 模板写入，L2 是 source of truth，正文采用分区结构：

| 区块 | 要求 |
|------|------|
| frontmatter | 字段齐全（尤其 `topic` 填目录名如 `3000-Agent`；`source` 填枚举值 url/manual/file/claude；`source_url` 填实际 URL；`status: draft`） |
| 核心提炼 | 用自己的话概括本文核心观点 |
| 关键概念 | 本文涉及的重要概念 wikilink 列表 |
| 原文要点 | 章节大纲 + 关键论点，非全文搬运 |
| 来源 | 作者、机构、原文链接、原始文件 |
| 原文笔记 | `---` 分隔后的原文中文翻译，保留段落层次 |

- `title` 保留原始标题；slug 仅用于文件名
- `tags`：5-10 个，无空格，多词连字符，**inline 格式** `[tag1, tag2]`
- `summary`：200 字以上
- `resource_refs`：与正文 `![[...]]` 1:1

### 6. 判断 L3 触发（阻塞确认步骤）

L3 由 L2 派生，逐个检查可派生的 concept/entity/comparison。

**必须先输出 L3 创建计划表，等用户确认后才能创建任何 L3 文件：**

| # | 类型 | slug | processing_path | 目录 | 理由 |
|---|------|------|-----------------|------|------|
| 1 | concept | agent-loop | AI技术/Agent | `0102/agent/` | 独立机制 |
| 2 | concept | transformer-architecture | AI技术/LLM基础 | `0102/llm-basics/` | 跨域独立概念 |
| 3 | entity | DALL-E | AI技术/图像生成 | `0103/product/` | 独立产品 |

| 类型 | 触发条件 |
|------|---------|
| concept | 满足其一：独立机制 / 跨源引用≥2 / 工具价值 |
| entity | 独立产品/平台/组织/人物/论文 |
| comparison | 差异/取舍 |

不建 L3：教科书分类列举、纯对比关系（→ comparison）、已有概念的子细节（→ 合入已有 concept）。

**用户确认操作：**
- **确认全部**：按计划落盘
- **调整目录**：修改某个 L3 的 processing_path 和目录
- **删除**：某个 L3 不需要创建
- **新增**：补充遗漏的 L3
- **合并**：把 2+ 个 L3 合为一个

**未获用户确认前，禁止创建任何 L3 文件。**

一个 L2 可派生多个不同 topic 的 L3。
0101 路径由 topics.yaml 大类映射决定（如 `3000-Agent` → AI技术 → `0101/AI技术/Agent.md`）。

**L3 文件名 slug 规则**：
- 全小写英文 kebab-case（如 `agent-loop.md`，非 `AgentLoop.md`）
- entity 文件名也全小写（如 `crewai.md`，非 `CrewAI.md`）
- 专有名词保留原形仅小写（如 `llm-judge.md`，非 `LLMJudge.md`）

**L3 目录规则**：
- entity 子目录全小写（如 `0103-wiki-entities/product/`，非 `Product/`）
- comparison 子目录全小写英文 slug（如 `0104-wiki-comparisons/automation-paradigm/`，非 `自动化范式/`）

**Topic 页面完整性**：创建或更新 topic 页面时，必须列出所有本次创建的关联 L3（concept + entity + comparison），确保无遗漏。

### 7. L3 合并规则

同 slug 匹配→合并：新信息补充、冲突标注、source 追加、更新 updated。

### 8. 死链治理
> 模型：此步骤可用 Haiku。

**L2 正文**：正式 [[wikilink]] 正常使用；未建概念同时写入 frontmatter `planned_links`。

**L3 正文**：扫描每个 L3 文件正文中的所有 [[wikilink]]，逐一确认：
- 已存在的 L3 文件 → 正常使用
- 不存在的 → 写入该文件的 `planned_links`（纯 slug 字符串，如 `planning`，非 `[[planning]]`）

### 9. 跨主题引用 + 更新配置

- tags 重叠≥2 且无 wikilink→建议关联
- 新建主题目录→追加到 `0100-wiki-meta/configs/topics.yaml`
- 新标签：列出所有新 tag 清单表（tag / 语言 / 是否有近似 tag），**用户逐个确认或批量确认后**再追加到 `0100-wiki-meta/configs/tag-vocabulary.yaml`

### 10. 写入前强制校验（阻塞步骤）
> 模型：此步骤可用 Haiku。

**以下每一项必须通过，否则不得写入：**

| # | 检查项 | 依据 |
|---|--------|------|
| 1 | `topic` 匹配 `^\d{4}-.+$`（如 `3000-Agent`） | schema.yaml L2 |
| 2 | `source` 是枚举值（url/manual/file/claude），非 URL 字符串 | schema.yaml L2 |
| 3 | `tags` ≥5 个，无空格，inline 格式 `[t1, t2]` | schema.yaml L2 |
| 4 | `summary` 200 字以上 | schema.yaml L2 |
| 5 | `status: draft`（首次创建默认 draft） | schema.yaml L2 |
| 6 | L3 `processing_path` 匹配 `^\S+/\S+$`（如 `AI技术/Agent`） | schema.yaml L3 |
| 7 | L3 `tags` ≥5 个 | schema.yaml L3 |
| 8 | L3 `summary` 200 字以上 | schema.yaml L3 |
| 9 | 0101 topic 综述已创建或更新，且列出了所有关联 L3 | 规则 |
| 10 | config 文件已更新（如有新主题/新标签） | 规则 |
| 11 | 所有 L3 正文 wikilink 已扫描，死链已写入 planned_links | 步骤 8 |
| 12 | L3 文件名和子目录均为全小写英文 slug | 命名规则 |

### 11. 操作日志 + 报告收尾

询问是否移入 `.trash/`（D008），确认后执行 git commit。
