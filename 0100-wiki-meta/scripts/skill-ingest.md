# skill-ingest：知识摄入（L1 → L2 → L3）

> 执行要求：开始前先用 TaskCreate 创建包含全部步骤(1-10)的 tasklist，每完成一步标记 completed。

> ⏱️ **执行时间预估**：
> - 单文件（无图片）：2-3 分钟
> - 单文件（含图片）：3-5 分钟
> - 图片较多或网络慢：5-10 分钟
> - ⚠️ 超过 10 分钟未完成 → 建议中断检查日志

## 触发方式

1. **单文件模式**：用户 `@` 引用单个 inbox 文件
2. **批量模式**：用户 `@` 引用多个文件，或 `@` 引用 `0003-inbox/` 目录

## 批量模式说明

### 智能分批建议

系统根据文件数量自动推荐处理方式：

| 文件数 | 推荐模式 | 预计决策数 | 质量保证 |
|--------|---------|-----------|---------|
| 1-2 | 批量模式 | 6-10 项 | ✓ 高 |
| 3-4 | **按主题分批** | 每批 8-12 项 | ✓ 高 |
| 5+ | **逐个处理** | 每次 3-5 项 | ✓ 最高 |

> ⚠️ **质量优先原则**：批量模式会增加决策负荷，可能导致：
> - 决策疲劳：信息过载 → 快速浏览 → 遗漏细节
> - 上下文切换：频繁切换文件理解 → 决策质量下降
> - 误判合并：全局去重可能合并语义不同的概念
>
> **建议**：
> - 重要笔记/复杂内容 → 逐个处理
> - 相关主题素材 → 小批量（2-3 个文件）
> - 简单素材/清理任务 → 可批量（需仔细审查合并项）

### 处理流程

**阶段 1（并行预处理）**：
- 每个文件独立执行步骤 1-5（推荐、下载、评分）
- 生成各自的待写入清单
- 无副作用，可并行执行

**阶段 2a（L2 审查点）**：
- 展示 L2 计划表（主题、slug、tags）
- 用户逐行审查，专注 L2 质量
- 确认后进入 L3 审查

**阶段 2b（L3 审查点）**：
- 展示 L3 计划表，重点标注：
  - 评分 5-6 的边界案例（用户决定）
  - 标记"已合并"的 L3（展开查看合并理由和来源文件）
  - 相似度 0.7-0.85 的"相关概念"（可能误判）
- 用户逐行审查，确认或调整

**阶段 3（统一写入）**：
- 串行执行步骤 6-10（避免配置文件竞争）
- 单次 git commit 包含所有变更

**分批建议示例**：
```
检测到 5 个文件，按主题分批建议：
  批次 1: file1.md, file2.md (主题: Agent, 预计 8 项决策)
  批次 2: file3.md, file4.md (主题: RAG, 预计 10 项决策)
  批次 3: file5.md (主题: 图像生成, 预计 4 项决策)

选择：
1. 按推荐分批执行 ⭐️ (质量最优)
2. 全部批量处理 (预计 35 项决策，不推荐)
3. 逐个处理 (最高质量，耗时较长)
```

---

## 前置检查

### 步骤 0：GateGuard 检测与用户确认

**IMPORTANT**: 在开始 ingest 流程前，检测 GateGuard 状态并交由用户决策。

```
检测到 ingest 流程，GateGuard 可能阻塞批量文件创建。
是否临时禁用 GateGuard？

选项：
1. 禁用 GateGuard（推荐）⭐️ — 提升执行效率，ingest 已有多层校验
2. 保持启用 — 每个新文件需确认（预计增加 5-10 分钟）
```

**如果用户选择禁用**：记录到执行日志，继续后续步骤
**如果用户选择保持启用**：正常执行，遇到阻塞时逐个满足要求

### 步骤 0.3：Delta 跟踪检查

**检查文件是否已摄入**：
```bash
python "D:\obsidian\0100-wiki-meta\scripts\delta-track.py" check "$SOURCE_FILE"
```

**如果文件已摄入**：
```
⚠️  检测到文件已摄入：inbox/agent-basics.md
  上次摄入: 2026-07-05 10:30:00
  内容哈希: abc123def
  产出页面: 3 个 (2 L2 + 1 L3)

是否重新处理？
1. 跳过（使用已有内容）⭐️
2. 增量更新（检测内容变化）
3. 完全重新摄入
```

### 步骤 0.5：用户决策图片和翻译

**IMPORTANT**: 询问用户处理偏好。

```
📋 请选择处理方式：

图片：1. 下载到本地 ⭐️  2. 跳过（保留 URL）
翻译：1. 完整翻译 ⭐️（5-10分钟） 2. 保留原文（2-3分钟）
```

### 文件检查

**单文件模式**：
1. 确认目标文件在 `0003-inbox/` 下且存在
2. 读取全文，提取标题、来源、核心内容
3. 扫描原文中的图片引用

**批量模式**：
1. 如果 `@` 引用的是目录，执行 `find 0003-inbox/ -type f -name "*.md"` 列出所有文件
2. 过滤掉 `.trash/` 子目录和非 markdown 文件
3. 展示文件列表（序号 + 文件名 + 修改时间），用户确认处理范围
4. 对每个文件执行前置检查（读取、扫描图片）

## 执行步骤

> **进度可视化**：每个步骤开始时输出 `## [N/10] 步骤名称`

### 1. 主题目录与 slug 推荐（合并确认）
> 模型：此步骤可用 Haiku。

**⚠️ IMPORTANT: 必须使用 AskUserQuestion 工具进行交互式确认，禁止使用纯文本输出。**

#### 1a. 主题目录推荐（必须使用 AskUserQuestion）

**推荐逻辑**：
- 对照 `0100-wiki-meta/configs/topics.yaml`
- 给出 3-5 推荐选项，每个附理由（匹配度、已有相关笔记数）
- 格式：`{编号}-{显示名}`（如 `3000-Agent`）
- 边界主题/多主题交叉标注
- 无匹配时建议新建主题目录

**AskUserQuestion 参数设计**：
- **question**: "请选择该笔记的主题目录（L2 归属）"
- **header**: "主题目录"
- **multiSelect**: false
- **options**: 3-5 个推荐，每个包含：
  - **label**: 目录名（如 `3000-Agent`）+ `⭐️` 标记推荐项
  - **description**: 匹配度 + 已有笔记数 + 核心关键词

**示例调用**：
```json
{
  "questions": [{
    "question": "请选择该笔记的主题目录（L2 归属）",
    "header": "主题目录",
    "multiSelect": false,
    "options": [
      {
        "label": "3000-Agent ⭐️",
        "description": "匹配度 95%，已有 12 篇。关键词：agent-loop, reasoning, planning"
      },
      {
        "label": "3200-LLM基础",
        "description": "匹配度 60%，已有 8 篇。涉及 Transformer 底层架构"
      },
      {
        "label": "新建: 3050-Multi-Agent",
        "description": "当前无此主题，建议新建专注多智能体协作"
      }
    ]
  }]
}
```

#### 1b. 文件名 slug 推荐（必须使用 AskUserQuestion）

**推荐逻辑**：
- 文件名转换：空格→`-`，`.`→`_`，特殊字符→`_`
- 全英文 kebab-case 全小写（title 字段用中文）
- 3-5 推荐选项，每个附理由（简洁度、语义准确度）
- `rg --files` 查重，重名追加 `-2`/`-3`

**AskUserQuestion 参数设计**：
- **question**: "请选择文件名（slug，仅用于文件名，title 保留中文原文）"
- **header**: "文件名"
- **multiSelect**: false
- **options**: 3-5 个推荐，每个包含：
  - **label**: 文件名（如 `agent-loop.md`）+ `⭐️` 标记推荐项
  - **description**: 简洁度 + 语义准确度 + 查重结果

**示例调用**：
```json
{
  "questions": [{
    "question": "请选择文件名（slug，仅用于文件名，title 保留中文原文）",
    "header": "文件名",
    "multiSelect": false,
    "options": [
      {
        "label": "agent-loop.md ⭐️",
        "description": "简洁，核心术语，无重名冲突"
      },
      {
        "label": "agent-execution-cycle.md",
        "description": "完整描述执行周期，更具可读性"
      },
      {
        "label": "autonomous-agent-loop.md",
        "description": "强调自主性，区分传统循环模式"
      }
    ]
  }]
}
```

### 2. 处理图片资源

**IMPORTANT**: 根据步骤 0.5 用户选择执行。

**如果用户选择下载图片**：
1. 扫描 L1 中的图片 URL
2. 逐张下载到 `0001-resource/{topic}/{slug}-{timestamp}.{ext}`
   - **命名格式**：`{slug}-{timestamp}.{ext}`，其中 timestamp 格式为 `YYYYMMDDHHmmss`
   - 示例：`0001-resource/3000-Agent/agent-loop-20260706132245.png`
   - **废弃格式**：不再使用序号格式（如 `agent-loop-01.png`）
   - **超时控制**：单张图片下载超时 30 秒
   - **失败处理**：下载失败 → 记录到 frontmatter `failed_images: [url1, url2]`，继续执行（用户可事后手动下载）
   - **建议**：可并行下载多张图片以提升效率
3. 正文远程引用改写为 `![[0001-resource/...]]`（失败图片保留原 URL）
4. 写入 `resource_refs`，与正文 1:1 对齐（仅包含成功下载的图片）
5. 无图片则 `resource_refs: []`

### 3. 生成 id 与 content_hash

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

### 4. 创建 L2

**IMPORTANT**: 根据步骤 0.5 用户选择执行翻译。

> 翻译：原文中译使用 Haiku 模型，分段 prompt "翻译为中文，保留技术术语和段落结构"。

按 `t-knowledge.md` 模板写入，L2 是 source of truth，正文采用分区结构：

| 区块 | 要求 |
|------|------|
| frontmatter | 字段齐全（尤其 `topic` 填目录名如 `3000-Agent`；`source` 填枚举值 url/manual/file/claude；`source_url` 填实际 URL；`status: draft`） |
| 核心提炼 | 用自己的话概括本文核心观点（中文） |
| 关键概念 | 本文涉及的重要概念 wikilink 列表（中文） |
| 原文要点 | 章节大纲 + 关键论点，非全文搬运（中文） |
| 来源 | 作者、机构、原文链接、原始文件 |
| 原文笔记 | `---` 分隔后的原文。**用户选择"完整翻译"**：翻译为中文；**用户选择"保留原文"**：保留原语言 |

- `title` 保留原始标题；slug 仅用于文件名
- `tags`：5-10 个，无空格，多词连字符，**inline 格式** `[tag1, tag2]`
- `summary`：200 字以上
- `resource_refs`：与正文 `![[...]]` 1:1

### 5. 判断 L3 触发（阻塞确认步骤）

L3 由 L2 派生，逐个检查可派生的 concept/entity/comparison。

**前置检查**：
1. **语义去重**：`rg --files 0102/` 检索已存在的 L3，用语义相似度判断是否重复
   - 相似度 >0.85 → 提示"可能与 [[existing-concept]] 重复，建议合并"
   - 相似度 0.7-0.85 → 提示"与 [[existing-concept]] 相关，确认是否独立"

2. **L3 重定位检测**：检查是否需要移动已存在的 L3 文件
   - 如果检测到 L3 文件 X 已存在（同 slug）
   - 分析新 L2 内容建议的 processing_path 和目录
   - 对比现有文件的物理目录与新建议目录
   - **触发重定位提示**：物理目录不同 + 标签匹配度≥2
   - 给出三选一：保持原位 / 移动到新位置 / 两者都保留（拆分）

3. **子分类推荐**：参考 `l3-structure.yaml` 的 `examples` 和 `criteria`
   - 给出 3 个候选子分类 + 匹配理由
   - 示例：`core/`（匹配 criteria: "Agent 运行的基础组件"）

**评分模型（0-10分）**：
- 有独立定义段落：+3
- 有代码示例：+2
- 有配图说明：+1
- 在多处被引用：+2
- 是领域核心术语：+2
- **≥6分**：推荐创建；**3-5分**：由用户决定；**<3分**：不建议
- **过细节扣分**：如果是已有概念的子步骤（如"初始化循环状态"属于"agent-loop"） → -3分

**⚠️ IMPORTANT: 必须先展示完整的L3创建计划表（含最终存储位置），再使用AskUserQuestion确认。等待用户明确确认后才能创建任何L3文件。**

#### L3创建计划表格式（必须包含完整存储路径）

每个L3候选项必须包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| # | 序号 | 1 |
| 类型 | concept/entity/comparison | concept |
| slug | 文件名（全小写kebab-case） | `agent-loop.md` |
| 评分 | 0-10（≥6推荐，3-5待定，<3不建议） | 8 |
| 子分类 | 推荐子目录 | `core/` ⭐️ |
| processing_path | 知识域路径 | `AI技术/Agent` |
| **最终存储位置** | **完整物理路径（含子分类+文件名）** | **`0102-wiki-concepts/agent/core/agent-loop.md`** |
| 理由 | 创建依据 | 独立定义+代码+术语 |
| 相似概念 | 已有相似项（相似度） | 无 或 `agent-state (0.72)` |

**展示示例**：

```markdown
## 📋 L3 创建计划表

| # | 类型 | slug | 评分 | 子分类 | processing_path | **最终存储位置** | 理由 | 相似 |
|---|------|------|------|--------|----------------|-----------------|------|------|
| 1 | concept | agent-loop.md | 8 | core/ ⭐️ | AI技术/Agent | **`0102-wiki-concepts/agent/core/agent-loop.md`** | 独立定义+代码+术语 | 无 |
| 2 | concept | transformer.md | 7 | architecture/ ⭐️ | AI技术/LLM基础 | **`0102-wiki-concepts/llm-basics/architecture/transformer.md`** | 独立定义+配图 | 无 |
| 3 | entity | dall-e.md | 6 | - | AI技术/图像生成 | **`0103-wiki-entities/product/dall-e.md`** | 独立产品 | 无 |
| 4 | comparison | agent-vs-workflow.md | 6 | automation-paradigm/ | AI技术/Agent | **`0104-wiki-comparisons/automation-paradigm/agent-vs-workflow.md`** | 两种范式对比 | 无 |
| 5 | concept | loop-init.md | 2 | core/ | AI技术/Agent | **`0102-wiki-concepts/agent/core/loop-init.md`** | ❌ 过细节（属于agent-loop内部） | agent-loop (0.92) |

**评分说明**：≥6分推荐创建，3-5分边界案例，<3分不建议
```

**然后使用AskUserQuestion批量确认**：

```json
{
  "questions": [{
    "question": "请确认L3创建计划（已展示完整存储路径）",
    "header": "L3确认",
    "multiSelect": false,
    "options": [
      {
        "label": "确认全部推荐项（#1, #2, #3, #4）⭐️",
        "description": "创建所有评分≥6的L3，使用上述推荐的存储位置"
      },
      {
        "label": "仅创建高分项（#1, #2）",
        "description": "只创建评分≥7的L3"
      },
      {
        "label": "自定义选择",
        "description": "我将指定具体要创建的L3序号或调整存储位置"
      }
    ]
  }]
}
```

不建L3：评分<3、教科书分类列举、纯对比关系（→ comparison）、已有概念的子细节（→ 合入已有concept）。

**用户确认操作说明：**
- **确认全部推荐项**：创建所有评分≥6的L3，使用表格中展示的最终存储位置
- **仅创建高分项**：只创建评分≥7的L3
- **自定义选择**：用户可以：
  - 指定具体序号（如"只创建#1和#3"）
  - 调整某个L3的存储位置（如"#2改到llm-basics/core/"）
  - 删除某个推荐项
  - 补充新的L3概念

**未获用户确认前，禁止创建任何L3文件。**

一个 L2 可派生多个不同 topic 的 L3。
0101 路径由 topics.yaml 大类映射决定（如 `3000-Agent` → AI技术 → `0101/AI技术/Agent.md`）。

**L3 文件名 slug 规则**：
- 全小写英文 kebab-case（如 `agent-loop.md`，非 `AgentLoop.md`）
- entity 文件名也全小写（如 `crewai.md`，非 `CrewAI.md`）
- 专有名词保留原形仅小写（如 `llm-judge.md`，非 `LLMJudge.md`）
- 正文 wikilink 也用全小写 slug（`[[claude-code]]`），需显示原名时用别名（`[[claude-code|Claude Code]]`）

**L3 目录规则**：
- concept 支持子分类（如 `0102/agent/core/`、`0102/agent/frameworks/`）
- entity 子目录全小写（如 `0103/product/`，非 `Product/`）
- comparison 子目录全小写英文 slug（如 `0104/automation-paradigm/`，非 `自动化范式/`）

**Topic 页面完整性**：创建或更新 topic 页面时，必须列出所有本次创建的关联 L3（concept + entity + comparison），确保无遗漏。

#### 5d. 识别类型化关系（E5）

创建L3时，扫描L2原文和L3内容，识别明确的语义关系模式：

| 关键词模式 | 关系类型 | 示例 |
|-----------|---------|------|
| "X基于Y"、"X派生自Y" | derived_from | Transformer派生自Attention |
| "X替代了Y"、"X取代Y" | replaces | BERT替代了LSTM |
| "X使用Y"、"X调用Y" | uses | Agent使用Tool |
| "X扩展了Y" | extends | GPT-4扩展了GPT-3 |
| "X实现了Y" | implements | BERT实现了预训练 |
| "X与Y相反"、"X矛盾Y" | contradicts | 集中式与分布式矛盾 |
| 其他语义关联 | related_to | 默认类型 |

**写入L3 frontmatter**：
```yaml
relationships:
  - target: "[[attention-mechanism]]"
    type: derived_from
  - target: "[[lstm]]"
    type: replaces
```

**注意**：
- 仅在有明确语义关系时添加，不强制
- target使用wikilink格式（`[[slug]]`）
- 关系将被index-notes.py自动提取到SQLite relationships表

### 6. L3 合并规则

同 slug 匹配→合并：新信息补充、冲突标注、source 追加、更新 updated。

### 7. 死链治理
> 模型：此步骤可用 Haiku。

**L2 正文**：正式 [[wikilink]] 正常使用；未建概念同时写入 frontmatter `planned_links`。

**L3 正文**：扫描每个 L3 文件正文中的所有 [[wikilink]]，逐一确认：
- 已存在的 L3 文件 → 正常使用
- 不存在的 → 写入该文件的 `planned_links`（纯 slug 字符串，如 `planning`，非 `[[planning]]`）

### 8. 跨主题引用 + 更新配置

#### 8a. 新标签确认（必须使用AskUserQuestion）

**⚠️ IMPORTANT: 必须使用AskUserQuestion工具展示新标签清单表，等待用户确认后才能追加到tag-vocabulary.yaml。**

**检测流程**：
1. 扫描本次ingest的所有L2/L3的`tags`字段
2. 对比`0100-wiki-meta/configs/tag-vocabulary.yaml`，识别未登记的新标签
3. 对每个新标签检查近似标签（编辑距离≤2或语义相似>0.8）
4. 检查格式规范（全小写、连字符、无空格、非混合语言）

**第一步：展示新标签清单表**

```markdown
## 🏷️ 新标签清单

| # | 新标签 | 语言 | 近似标签（相似度） | 建议操作 |
|---|--------|------|-------------------|---------|
| 1 | agent-loop | 英文 | - | ✅ 新增 |
| 2 | multi-agent-system | 英文 | multi-agent (0.85) | ⚠️ 可能重复 |
| 3 | transformer-架构 | 混合 | transformer-architecture | ❌ 格式错误 |
```

**第二步：使用AskUserQuestion批量确认**

```json
{
  "questions": [{
    "question": "请确认新标签的处理方式",
    "header": "标签确认",
    "multiSelect": false,
    "options": [
      {
        "label": "智能处理（推荐）⭐️",
        "description": "新增#1，跳过#2使用已有multi-agent，修正#3为transformer-architecture"
      },
      {
        "label": "全部新增",
        "description": "将所有新标签原样添加到tag-vocabulary.yaml（不推荐，可能引入重复）"
      },
      {
        "label": "逐个确认",
        "description": "我将对每个新标签单独决策"
      }
    ]
  }]
}
```

**如果用户选择"逐个确认"**，对有问题的标签追加单独确认：

```json
{
  "questions": [{
    "question": "标签'multi-agent-system'与已有'multi-agent'相似度0.85，如何处理？",
    "header": "标签#2",
    "multiSelect": false,
    "options": [
      {
        "label": "使用已有'multi-agent'",
        "description": "替换为已登记标签，避免重复"
      },
      {
        "label": "新增'multi-agent-system'",
        "description": "作为独立标签登记（需说明与multi-agent的区别）"
      }
    ]
  }]
}
```

#### 8b. 跨主题引用检查

- tags 重叠≥2 且无 wikilink→建议关联
- 新建主题目录→追加到 `0100-wiki-meta/configs/topics.yaml`

### 9. 写入前强制校验（阻塞步骤）
> 模型：此步骤可用 Haiku。

**以下每一项必须通过，否则不得写入：**

| # | 检查项 | 依据 |
|---|--------|------|
| 1 | `topic` 匹配 `^\d{4}-.+$`（如 `3000-Agent`） | schema.yaml L2 |
| 2 | `source` 是枚举值（url/manual/file/claude），非 URL 字符串 | schema.yaml L2 |
| 3 | `tags` ≥5 个，无空格，inline 格式 `[t1, t2]` | schema.yaml L2 |
| 4 | `summary` 200 字以上 | schema.yaml L2 |
| 5 | `status: published`（首次 ingest 校验全部通过后默认标记） | schema.yaml L2 |
| 6 | 所有 `tags` 均在 `tag-vocabulary.yaml` 中已登记 | 规则 |
| 7 | L3 `processing_path` 匹配 `^\S+/\S+$`（如 `AI技术/Agent`） | schema.yaml L3 |
| 8 | L3 `tags` ≥5 个 | schema.yaml L3 |
| 9 | L3 `summary` 200 字以上 | schema.yaml L3 |
| 10 | L3 所有 `tags` 均在 `tag-vocabulary.yaml` 中已登记 | 规则 |
| 11 | 0101 topic 综述已创建或更新，且列出了所有关联 L3 | 规则 |
| 12 | config 文件已更新（如有新主题/新标签） | 规则 |
| 13 | 所有 L3 正文 wikilink 已扫描，死链已写入 planned_links | 步骤 7 |
| 14 | L3 文件名和子目录均为全小写英文 slug | 命名规则 |

### 10. 更新索引 + 操作日志 + 热缓存 + 报告收尾

**更新 SQLite 索引**：
```bash
python "D:\obsidian\0100-wiki-meta\scripts\index-notes.py"
```

**验证索引完整性**：
```bash
# 确认笔记数量
sqlite3 .wiki.db "SELECT COUNT(*), layer FROM notes GROUP BY layer;"
# 确认 topics 已同步
sqlite3 .wiki.db "SELECT COUNT(*) FROM topics;"
# 确认标签关系
sqlite3 .wiki.db "SELECT COUNT(*) FROM note_tags;"
```

**更新热缓存（hot.md）**：
```bash
# 添加本次创建的 L2/L3 到热缓存
# 示例：python update-hot.py add-l2 "3000-Agent/agent-basics.md"
for l2_path in ${新建的L2路径列表[@]}; do
  python "D:\obsidian\0100-wiki-meta\scripts\update-hot.py" add-l2 "$l2_path"
done

for l3_path in ${新建的L3路径列表[@]}; do
  python "D:\obsidian\0100-wiki-meta\scripts\update-hot.py" add-l3 "$l3_path"
done
```

询问是否移入 `.trash/`（D008），确认后执行 git commit。
