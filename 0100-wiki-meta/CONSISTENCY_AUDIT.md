# Skill文件与CLAUDE.md一致性分析报告

**审计日期**: 2026-07-10  
**审计范围**: 5个skill文件 vs CLAUDE.md"四操作规范"章节  
**总体评分**: ⚠️ 中度不一致（建议修复CLAUDE.md）

---

## 一、skill-ingest.md 一致性分析

### ✅ 一致项

1. **主题与slug推荐**
   - CLAUDE.md："判断归属主题目录（须用户确认）；生成slug"
   - skill-ingest.md：步骤1详细实现用户交互式选择
   - **一致**：都强制用户确认

2. **图片落地规则**
   - CLAUDE.md：`0001-resource/{topic}/{slug}/{timestamp}.{ext}`
   - skill-ingest.md 第2步：完全相同格式（timestamp 为 YYYYMMDDHHmmss）
   - **一致**

3. **L2正文分区结构**
   - CLAUDE.md：核心提炼+关键概念+原文要点+来源/原文笔记
   - skill-ingest.md 第4步：完全相同
   - **一致**

4. **L3派生判断与写入前校验**
   - CLAUDE.md：6、7步与skill-ingest.md 5、9步框架一致
   - **基本一致**

### ⚠️ 冲突项

#### 冲突1：图片路径格式 — **序号 vs 时间戳**
- **CLAUDE.md** 说法含糊不清：
  ```
  图片落地：…… `0001-resource/{topic}/{slug}-{timestamp}.{ext}`
  ```
  没明确 timestamp 格式

- **skill-ingest.md** 明确规定（第2步、第238行）：
  ```
  命名格式：{slug}-{timestamp}.{ext}，其中 timestamp 格式为 YYYYMMDDHHmmss
  示例：0001-resource/3000-Agent/agent-loop-20260706132245.png
  废弃格式：不再使用序号格式（如 `agent-loop-01.png`）
  ```

- **建议**：CLAUDE.md 应更新为明确的时间戳格式，且标记"废弃序号格式"

#### 冲突2：L3判断流程 — **简略 vs 详细**
- **CLAUDE.md** 第6步（L3触发）仅列举：
  - concept/entity/comparison 的判定规则（简述）
  - "是否建L3（满足其一：独立机制 / 跨源引用≥2 / 工具价值）"
  
- **skill-ingest.md** 第5步详细提供：
  - 评分模型（0-10分）：独立定义+3、代码示例+2、配图+1等
  - L3创建计划表（含最终存储位置）必须展示
  - 语义去重（相似度>0.85/0.7-0.85的处理）
  - L3重定位检测
  - 子分类推荐
  - 关系识别（relationships字段）

- **冲突点**：CLAUDE.md 没有提及：
  - ❌ 评分模型具体分值
  - ❌ 语义相似度检查（相似度0.85/0.7-0.85的阈值）
  - ❌ L3重定位提示
  - ❌ 关系识别（derived_from, replaces, uses等）

- **建议**：CLAUDE.md 应补充这些细节

#### 冲突3：新标签确认方式 — **集中 vs 分步**
- **CLAUDE.md** 第8b："tag-vocabulary.yaml — 本次 ingest 引入的新标签是否全部登记？"
  - 说法模糊，没说怎么处理

- **skill-ingest.md** 第8a（新标签确认）：
  - 第一步：展示新标签清单表（新标签+语言+近似标签+建议操作）
  - 第二步：使用 AskUserQuestion 批量确认（智能处理/全部新增/逐个确认）
  - 如选"逐个确认"，对相似标签追加单独交互

- **冲突点**：CLAUDE.md 没有提供交互式确认的流程
- **建议**：CLAUDE.md 应补充 AskUserQuestion 的使用

#### 冲突4：步骤顺序与完整性
- **CLAUDE.md** 的9步 vs skill-ingest.md 的10步
- **skill-ingest.md 新增**：
  - 步骤0：GateGuard检测
  - 步骤0.3：Delta跟踪检查（检查文件是否已摄入）
  - 步骤0.5：用户决策图片和翻译
  - 关系识别（5d）
  - hot.md更新（第10步）

- **冲突点**：CLAUDE.md 完全遗漏了这些步骤
- **建议**：CLAUDE.md 应补充这些前置和收尾步骤

### 📝 建议

1. **更新CLAUDE.md图片路径规则**：
   ```
   图片落地：…… `0001-resource/{topic}/{slug}-{YYYYMMDDHHmmss}.{ext}`
   [废弃] 不再使用序号格式如 agent-loop-01.png
   ```

2. **补充L3评分模型到CLAUDE.md**：
   - 有独立定义段落：+3
   - 有代码示例：+2
   - 有配图说明：+1
   - 被多处引用：+2
   - 是领域核心术语：+2
   - 过细节扣分：-3
   - ≥6分推荐，3-5分待定，<3分不建议

3. **补充新标签确认交互到CLAUDE.md**：
   记录需要使用 AskUserQuestion 工具展示清单表并批量确认

4. **补充前置与收尾步骤**：
   - 步骤0：GateGuard检测
   - 步骤0.3：Delta跟踪（检查文件重复摄入）
   - 步骤10：hot.md更新

---

## 二、skill-query.md 一致性分析

### ✅ 一致项

1. **分层检索优先级**
   - CLAUDE.md："L3（topic 优先）→ L2 → L1"
   - skill-query.md 步骤3："先读取L3概念页 → 需要细节则回溯L2 → 合成回答"
   - **一致**

### ⚠️ 重大冲突

#### 冲突1：检索方式 — **手动grep vs 自动SQLite**（核心矛盾）

- **CLAUDE.md** Query部分（简述）：
  ```
  1. rg 0101 找主题域 → 域内 rg 0102-0104
  2. 无匹配 → 全局 rg → L2 → L1
  3. Top 8 全文，引用 [[wikilink]]
  ```
  **方式**：通过 ripgrep（文本搜索）手动执行

- **skill-query.md** 步骤2（SQLite FTS5检索）：
  ```bash
  python "D:\obsidian\0100-wiki-meta\scripts\query.py" "<关键词>" 8
  ```
  **方式**：SQLite全文检索 + 多因子排序 + 缓存优化

- **冲突本质**：
  - CLAUDE.md 假设用手工 rg 命令
  - skill-query.md 已实现自动化Python脚本

- **影响范围**：**VERY HIGH** — 这不是格式差异，是查询方式的根本不同

#### 冲突2：排序算法 — **无排序 vs 多因子排序**

- **CLAUDE.md**：没有提及任何排序算法

- **skill-query.md** 步骤2详细说明：
  - 文本相关性（50%）— FTS5 rank归一化
  - 入链数量（25%）— 页面权威度
  - 新鲜度（15%）— 30天内=1.0，90天内=0.5
  - 质量（10%）— published=1.0，draft=0.7

- **冲突**：CLAUDE.md 完全没有这套排序体系
- **建议**：CLAUDE.md 应补充或引用skill-query.md的排序说明

#### 冲突3：热缓存机制 — **无 vs 有**

- **CLAUDE.md**：完全没有提及缓存

- **skill-query.md** 步骤1（热缓存）：
  - 优先读取 `hot.md`
  - 记录最近72h的高频查询结果
  - 可节省60%+token

- **冲突**：CLAUDE.md 应补充或说明是否需要热缓存

### 📝 建议

1. **CLAUDE.md的Query部分需完全重写**（或改为直接参考skill-query.md）

2. **更新Query流程**：
   ```
   步骤1：读热缓存 → hit → 返回
   步骤2：SQLite FTS5（多因子排序）
   步骤3：读取相关页面 + 生成回答
   步骤4：返回结果并引用wikilink
   ```

3. **新增排序说明**：四因子权重（50/25/15/10）

---

## 三、skill-update.md 一致性分析

### ✅ 一致项

1. **变更分级**
   - CLAUDE.md：轻微/中等/重大三级
   - skill-update.md：完全相同
   - **一致**

2. **L3编辑限制**
   - CLAUDE.md："L3不可人工编辑（D010）"
   - skill-update.md 第45行："L3编辑限制（D010）"
   - **一致**

3. **Wikilink影响分析**
   - CLAUDE.md 重大变更："rg wikilink 引用 → rg L3 source → 同步"
   - skill-update.md 步骤4-7：逐步实现
   - **基本一致**

### ⚠️ 冲突项

#### 冲突1：content_hash更新 — **无 vs 有**

- **CLAUDE.md**：第8步"配置同步"中未提及content_hash

- **skill-update.md** 明确说明（步骤轻微/中等/重大变更处）：
  ```bash
  若修改了正文，更新 content_hash:
  python3 -c "import hashlib,re; c=open(path,'r').read(); body=re.split(r'^---\s*$',c,maxsplit=2,flags=re.MULTILINE)[2] if c.startswith('---') else c; print(hashlib.sha256(body.encode()).hexdigest()[:8])"
  ```

- **冲突**：CLAUDE.md 应补充content_hash更新规则

#### 冲突2：LOG记录细节 — **简略 vs 明确**

- **CLAUDE.md**："更新 updated → LOG"

- **skill-update.md**：
  - 轻微：改正文 → updated → LOG → git commit
  - 中等：改Frontmatter → updated → LOG → git commit
  - 重大：先输出受影响范围 → 用户确认 → 然后修改 → 同步 → LOG → git commit

- **冲突**：skill-update.md 更强调user confirmation和受影响范围分析
- **建议**：CLAUDE.md 应补充这些细节

### 📝 建议

补充到CLAUDE.md：
1. content_hash更新命令
2. 重大变更前先输出"受影响范围报告"
3. 用户确认后才执行修改

---

## 四、skill-remove.md 一致性分析

### ⚠️ 严重不一致 — **CLAUDE.md极其简略**

- **CLAUDE.md** 中的Remove部分：
  ```
  ### Remove（L2 及派生数据清理）
  > 详见 `0100-wiki-meta/scripts/skill-remove.md`
  删除 L2 文件并清理所有派生数据（L3、资源、配置、索引）。
  触发场景：…… （仅3行）
  流程：识别分析 → 用户确认 → 执行删除（移入 .trash/） → 验证日志
  ```

- **skill-remove.md** 提供详细流程（900+行）：
  - Phase1：追溯派生关系（方法1/2/3三重验证）
  - Phase2：用户确认（强制确认点）
  - Phase3：执行删除（备份批次+移动文件+处理死链+清理配置+更新DB）
  - Phase4：验证与日志
  - 边界情况处理（5种）
  - 安全检查清单

### 📝 建议

CLAUDE.md 中Remove部分已正确指向 skill-remove.md（"详见"），**无需修改**。但应注意：
- skill-remove.md 的复杂度远超CLAUDE.md的简述
- 确保执行时严格按skill-remove.md流程，不能简化

---

## 五、skill-lint.md 一致性分析

### ✅ 一致项

1. **检查项覆盖率**
   - CLAUDE.md列举12个报告项
   - skill-lint.md覆盖所有+更多

2. **自动修复：断裂wikilink**
   - CLAUDE.md："自动修复：断裂 wikilink"
   - skill-lint.md 第1步："不存在 → 标记 `<!-- BROKEN: [[目标]] -->`"
   - **一致**

### ⚠️ 冲突项

#### 冲突1：模型约束 — **无 vs 明确**

- **CLAUDE.md**："Lint 和翻译操作使用 Haiku 模型"（在系统概述中）

- **skill-lint.md** 明确重申（第4行）：
  ```
  > 模型约束：Lint 检查必须使用 Haiku 模型。
  ```

- **一致性评价**：✅ 一致，但skill-lint.md更明确

#### 冲突2：SQLite同步与一致性 — **无 vs 详细**

- **CLAUDE.md**：没有提及SQLite同步机制

- **skill-lint.md** 步骤0详细说明：
  - 0.1 文件存在性检查（DB中的文件是否都存在）
  - 0.2 索引完整性检查（本地文件是否都已索引）
  - 0.3 数量检查（LOCAL_COUNT ≠ DB_COUNT）
  - 0.4 自动同步（调用index-notes.py）
  - 0.5 标签词表同步检查

- **冲突**：CLAUDE.md 没有这套同步机制的描述
- **建议**：CLAUDE.md 应补充"步骤0：前置同步检查"

#### 冲突3：检查项顺序与优先级 — **无 vs 明确**

- **CLAUDE.md**：12个报告项列成表格，无优先级区分

- **skill-lint.md**：
  - 自动修复：断裂wikilink（高优先级）
  - 人工确认项：15项（按复杂度排序）

- **冲突**：CLAUDE.md 应区分"自动"vs"报告"
- **建议**：CLAUDE.md 应补充优先级区分

### 📝 建议

补充到CLAUDE.md：
1. 步骤0：前置SQLite同步检查
2. 标签词表同步检查
3. 区分"自动修复"vs"人工报告"的项目

---

## 六、综合评分与优先级建议

| Skill文件 | 一致度 | 优先级 | 推荐行动 |
|----------|--------|--------|---------|
| ingest | 70% ⚠️ | **HIGH** | CLAUDE.md 补充L3评分/关系识别/GateGuard/Delta等 |
| query | 20% 🔴 | **CRITICAL** | CLAUDE.md Query部分需完全重写或直接引用skill-query.md |
| update | 80% ✅ | MEDIUM | CLAUDE.md 补充content_hash和受影响范围分析 |
| remove | 100% ✅ | LOW | CLAUDE.md 已正确指向skill-remove.md |
| lint | 85% ✅ | MEDIUM | CLAUDE.md 补充SQLite同步和优先级区分 |

---

## 七、关键发现

### 🚨 Critical Issue: Query模块

CLAUDE.md中的Query流程（"rg 0101 → rg 0102-0104 → rg → L2 → L1"）与实际skill-query.md完全不同：
- 前者：手工grep、无排序、无缓存
- 后者：自动SQLite、多因子排序、热缓存

**建议**：
1. 确认系统实现的是哪一套（应该是skill-query.md）
2. 完全更新CLAUDE.md的Query部分
3. 考虑删除CLAUDE.md中的grep伪代码

### 📋 Missing Documentation

CLAUDE.md遗漏的内容：
- ❌ L3评分模型（ingest步骤5）
- ❌ 关系识别字段（ingest步骤5d）
- ❌ SQLite同步机制（lint步骤0）
- ❌ 热缓存机制（query步骤1）
- ❌ 多因子排序（query步骤2）
- ❌ content_hash更新（update步骤）
- ❌ GateGuard检测（ingest步骤0）
- ❌ Delta跟踪（ingest步骤0.3）

### ✅ Well-Aligned Areas

- Remove操作（已正确引向skill-remove.md）
- L3编辑限制（D010）
- L2正文分区结构
- Wikilink引用治理基础框架

---

## 八、立即行动项

### 优先级1（本周完成）
1. 更新CLAUDE.md Query部分 — 引入SQLite/排序/缓存概念
2. CLAUDE.md ingest补充L3评分模型

### 优先级2（本月完成）
3. CLAUDE.md补充GateGuard/Delta前置步骤
4. CLAUDE.md补充关系识别（relationships）
5. CLAUDE.md补充SQLite同步机制

### 优先级3（文档完善）
6. CLAUDE.md补充content_hash更新说明
7. CLAUDE.md lint部分区分"自动"vs"报告"

---

**报告完成**  
生成时间：2026-07-10 01:27:18 UTC
