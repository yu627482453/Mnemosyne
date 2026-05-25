# skill-ingest：知识摄入（L1 → L2 → L3）

> 执行要求：开始前先用 TaskCreate 创建包含全部步骤(1-11)的 tasklist，每完成一步标记 completed。


> 触发：用户 `@` 引用 inbox 文件要求处理

## 前置检查

1. 确认目标文件在 `0003-inbox/` 下且存在
2. 读取全文，提取标题、来源、核心内容
3. 扫描原文中的图片引用

## 拆分判断

满足以下条件拆分为多个 L2：有独立标题层级、每个概念可独立成文、概念间有明确边界。
不拆分：内容紧密关联、信息量不足（<3 要点）、用户要求合并。

## 执行步骤

### 1. 判断归属主题目录

- 对照 `0100-wiki-meta/configs/topics.yaml`
- 推荐时同时给中英文选项（如 `AI技术/Agent`）
- **首次归档须用户确认**；边界主题/多主题交叉必须询问
- 无匹配：按 topics.yaml 规则创建，格式 `{4位编号}-{中文主题名}`

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
python3 || python -c "import hashlib,json; s=json.dumps({topic:'{topic}',slug:'{slug}',created:'{created}'},sort_keys=True); print(hashlib.sha256(s.encode()).hexdigest()[:8])"

# content_hash: 写完后对文件全文 SHA256[:8]
python3 || python -c "import hashlib; print(hashlib.sha256(open('{path}','rb').read()).hexdigest()[:8])"
```

### 5. 创建 L2

> 翻译：原文主体中译必须使用 Haiku 模型，分段 prompt "翻译为中文，保留技术术语和段落结构"。

按 `t-knowledge.md` 模板写入，L2 是 source of truth：

| 区块 | 要求 |
|------|------|
| frontmatter | 字段齐全（尤其 `topic` 填目录名如 `3000-Agent`；`source` 填枚举值 url/manual/file/claude；`source_url` 填实际 URL；`status: draft`） |
| 核心内容 | 1-2 段浓缩，帮助检索 |
| 文章要点 | 3 条以上 |
| **原文主体** | 高保真中文翻译，保留原文段落层次 |
| 来源 | 作者、机构、原文链接、原始文件 |

- `title` 保留原始标题；slug 仅用于文件名
- `tags`：5-10 个，无空格，多词连字符，**inline 格式** `[tag1, tag2]`
- `summary`：200-500 字
- `resource_refs`：与正文 `![[...]]` 1:1

### 6. 判断 L3 触发

L3 由 L2 派生，目录按类型：

| 类型 | 目录 | 触发条件 |
|------|------|---------|
| concept | `0102/{大类}/{主题域}/{slug}.md` | 机制/方法/原则/模式 |
| entity | `0103/{entity_type}/{slug}.md` | 独立产品/平台/组织/人物/论文 |
| comparison | `0104/{comparison_axis}/{slug}.md` | 差异/取舍 |

**entity/comparison 主动逐项检查**：不要因主轴是 concept 就跳过。

0101 路径由 topics.yaml 大类映射决定（如 `3000-Agent` → AI技术 → `0101/AI技术/Agent.md`）。

### 7. L3 合并规则

同 slug 匹配→合并：新信息补充、冲突标注、source 追加、更新 updated。

### 8. 死链治理
> 模型：此步骤可用 Haiku。

正式 [[wikilink]] 正常使用（Obsidian 灰色标记缺失）；未建概念同时写入 frontmatter `planned_links`

### 9. 跨主题引用 + 更新配置

- tags 重叠≥2 且无 wikilink→建议关联
- 新建主题目录→追加到 `0100-wiki-meta/configs/topics.yaml`
- 新标签（用户确认后）→追加到 `0100-wiki-meta/configs/tag-vocabulary.yaml`

### 10. 写入前强制校验（阻塞步骤）
> 模型：此步骤可用 Haiku。

**以下每一项必须通过，否则不得写入：**

| # | 检查项 | 依据 |
|---|--------|------|
| 1 | `topic` 匹配 `^\d{4}-.+$`（如 `3000-Agent`） | schema.yaml L2 |
| 2 | `source` 是枚举值（url/manual/file/claude），非 URL 字符串 | schema.yaml L2 |
| 3 | `tags` ≥5 个，无空格，inline 格式 `[t1, t2]` | schema.yaml L2 |
| 4 | `summary` 200-500 字 | schema.yaml L2 |
| 5 | `status: draft`（首次创建默认 draft） | schema.yaml L2 |
| 6 | L3 `processing_path` 匹配 `^\S+/\S+$`（如 `AI技术/Agent`） | schema.yaml L3 |
| 7 | L3 `tags` ≥5 个 | schema.yaml L3 |
| 8 | L3 `summary` 200-500 字 | schema.yaml L3 |
| 9 | 0101 topic 综述已创建或更新 | 规则 |
| 10 | config 文件已更新（如有新主题/新标签） | 规则 |

### 11. 操作日志 + 报告收尾

询问是否移入 `.trash/`（D008），确认后执行 git commit。
