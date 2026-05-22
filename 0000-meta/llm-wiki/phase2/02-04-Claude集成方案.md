# 2.4 Claude Code × Obsidian 集成方案

> 日期：2026-05-14 | 修订：2026-05-18（同步 03 详细流程）

## 一、集成模式选择

### 主通道：文件直读写

Claude Code 原生具备完整的文件系统读写能力（Read/Write/Edit/Grep/Glob），直接操作 vault 中的 `.md` 文件：

| 操作 | 方式 | 说明 |
|------|------|------|
| 读取笔记 | `Read` 工具 | 读取 inbox 或已有知识页面 |
| 写入笔记 | `Write` | 创建新知识页面 |
| 编辑笔记 | `Edit` | 更新 frontmatter 或正文 |
| 搜索内容 | `Grep` | 全文搜索（替代 `obsidian search`） |
| 查找文件 | `Glob` | 按文件名/路径查找 |

**优势**：零依赖、无需 Obsidian 运行、无需许可证、可靠。

### 辅助通道：CLI

当 Obsidian 运行时，CLI 提供文件读写不具备的能力：

| CLI 能力 | Claude 触发方式 | 用途 |
|----------|----------------|------|
| `obsidian backlinks` | Bash 工具 | 反向链接分析 |
| `obsidian links` | Bash 工具 | 出站链接检查 |
| `obsidian tags counts` | Bash 工具 | 标签统计 |
| `obsidian create --template` | Bash 工具 | 用模板创建笔记 |

## 二、交互工作流

### 三核心操作

```
┌─────────────────────────────────────────────────────┐
│  Ingest（摄入）                                      │
│    inbox/ 文件 → Claude 读取 → 清洗/分类/摘要       │
│    → 写入主题目录 → 更新 INDEX/CHANGELOG         │
├─────────────────────────────────────────────────────┤
│  Query（查询）                                       │
│    用户提问 → Grep/Glob 搜索 → 读相关页面            │
│    → 合成回答 + 引用链接                             │
├─────────────────────────────────────────────────────┤
│  Lint（检查）                                        │
│    检查索引一致性 → 死链接 → 孤立页面                 │
│    → 报告 + 自动修复                                 │
└─────────────────────────────────────────────────────┘
```

### Ingest 详细流程

```
1. 素材放入 0003-inbox/，用户 @引用
2. Claude 读取 → 判断归属主题目录
3. 不存在则直接新建并告知用户
4. Bash 取最大序号 +1 → 分配 ID（空目录从 00001 开始）
5. 按模板创建 {编号}-{序号}-{slug}.md
6. 判断是否更新 0101-0104 合成页面（满50条自动分页）
7. 追加 0109-log/LOG-YYYY-MM-DD.md
8. 报告结果，建议关联
9. 询问是否删除 inbox 原文件
```

### Query 详细流程

```
1. 用户提问
2. Claude Grep title/summary 字段 → 直接定位候选文件
3. 最多读入 8 个候选文件全文
4. 若 8 个不足以回答，提示缩小范围
5. 合成回答，引用 [[wikilink]]
6. 可选：存档到 outbox
```

### Lint 详细流程

```
1. 用户："检查 wiki 健康状态"
     ↓
2. Claude 比对 INDEX.md ↔ 实际文件 → 检查 wikilink → 孤立页面
     ↓
3. 自动修复：补全 INDEX 缺失条目、修正路径
     ↓
4. 报告需人工决策的问题
     ↓
5. 追加 0109-log/
```

## 三、提示词管理

提示词统一存放在 `0100-wiki-meta/scripts/`：

```
0100-wiki-meta/scripts/
├── prompt-ingest.md        # 知识摄入提示词
├── prompt-classify.md      # 自动分类提示词
├── prompt-link.md          # 关联建议提示词
├── prompt-query.md         # 知识查询提示词
├── prompt-lint.md          # 健康检查提示词
└── prompt-summarize.md     # 摘要生成提示词
```

### 提示词加载方式

用户在 Claude Code 中 `@` 引用提示词文件 + inbox 文件：
```
@"0100-wiki-meta/scripts/prompt-ingest.md" @"0003-inbox/新知识.md" 处理
```

或者直接调用（Claude 已知晓工作流后）：
```
处理 inbox 中的新知识
```

## 四、Claude Code 的 Obsidian 感知能力

| 能力 | 方式 | 说明 |
|------|------|------|
| 读写 frontmatter | Read/Edit YAML | 直接操作 `---` 包裹的 YAML 元数据 |
| 识别 wikilink | Grep `[[...]]` | 搜索双向链接引用 |
| 识别 Dataview | Grep `dataview` 代码块 | 读取 INDEX.md 中的查询 |
| 追踪附件路径 | Read 附件引用 | 确保 `0001-resource/` 路径正确 |
| 目录结构感知 | Glob 目录 | 理解 vault 的分层结构 |

## 五、与 Obsidian 运行时的关系

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Obsidian    │     │  Vault       │     │  Claude Code │
│  (GUI)       │────→│  (.md files) │←────│  (CLI)       │
│              │     │              │     │              │
│  编辑/浏览   │     │  共享文件     │     │  读写/搜索   │
│  实时预览    │     │  系统         │     │  加工/分析   │
└──────────────┘     └──────────────┘     └──────────────┘
       ↑                                       │
       │          Obsidian CLI                 │
       └───────────────────────────────────────┘
            (仅当 Obsidian 运行时可用)
```

**关键约束**：
- Claude Code 修改文件后，Obsidian 自动检测并刷新（文件系统监控）
- Obsidian 中修改笔记后，Claude Code 下次读取时自动看到最新内容
- 两者通过文件系统天然同步，无需额外集成层

## 六、2.4 结论

| 决策 | 内容 |
|------|------|
| **主集成模式** | 文件直读写（零依赖、最可靠） |
| **辅助模式** | CLI（反向链接、标签统计，需 Obsidian 运行） |
| **交互方式** | 手动触发，`@` 引用文件或自然语言指令 |
| **提示词** | `0100-wiki-meta/scripts/` 下独立管理 |
| **工作流** | Ingest / Query / Lint 三核心操作 |

**关键判断**：Claude Code 的文件读写能力足以覆盖 90% 的场景，CLI 仅在需要 Obsidian 独有分析能力时调用。不需要任何中间层或插件——vault 的文件系统就是集成接口。

---

