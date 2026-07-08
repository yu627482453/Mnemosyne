# Skill: Remove L2 及其派生数据

> 删除 L2 文件并清理由其 ingest 产生的所有相关数据（L3、资源、配置、索引）

## 触发场景

- 用户 @ 引用 L2 文件并要求删除
- 用户明确指出要删除某个主题下的 L2 数据
- 发现重复、错误或过时的 L2 数据需要清理

## 核心原则

1. **安全第一** — 删除前必须用户确认,展示完整影响范围
2. **完整清理** — 删除 L2 及其所有派生数据（L3、资源、配置）
3. **追溯关系** — 通过 L3 的 `source` 字段找到所有派生文件
4. **保留备份** — 所有删除的文件移入 `.trash/` 而非直接删除
5. **记录操作** — 在 LOG 中详细记录删除操作和影响范围

## 操作流程

### Phase 1: 识别与分析

#### 1.1 定位 L2 文件

用户 @ 引用或描述目标 L2 文件,读取 frontmatter 提取:
- `id`: 唯一标识符
- `title`: 标题
- `topic`: 所属主题目录
- `resource_refs`: 关联的资源文件列表
- `created`: 创建时间
- `tags`: 标签列表

#### 1.2 追溯派生关系

**多重验证机制** - 使用3种方法确保不遗漏：

**方法1: 搜索source字段**
```bash
rg -l --type md "source:.*{L2相对路径}" \
  0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/ \
  --glob "**/*.md"
```

**方法2: 搜索文件名匹配**（防止遗漏与L2同名的L3）
```bash
L2_BASENAME=$(basename "{L2文件}" .md)
find 0102-wiki-concepts/ 0103-wiki-entities/ 0104-wiki-comparisons/ \
  -name "${L2_BASENAME}.md" -type f
```

**方法3: 验证结果**
```bash
for l3 in ${found_l3_files[@]}; do
  rg -q "{L2相对路径}" "$l3" && echo "确认: $l3"
done
```

记录并去重:
- L3 concept列表
- L3 entity列表  
- L3 comparison列表

#### 1.3 分析影响范围

检查以下项目：

**资源文件**

从 `resource_refs` 获取资源列表，**逐个检查**引用数：

```bash
# 对每个资源文件
for resource in ${resource_refs[@]}; do
  resource_name=$(basename "$resource")
  
  # 统计有多少文件引用此资源
  ref_count=$(rg -l "$resource_name" --type md | wc -l)
  
  if [ $ref_count -eq 1 ]; then
    # 仅当前 L2 使用 → 独占，应删除
    echo "独占: $resource_name"
  elif [ $ref_count -gt 1 ]; then
    # 被其他文件使用 → 共享，保留
    echo "共享($ref_count): $resource_name"
  else
    # 无引用 → 孤立，应删除
    echo "孤立: $resource_name"
  fi
done
```

**⚠️ 注意**：粗粒度统计（如 `rg -c pattern`）会遗漏孤立资源，必须逐个检查

**Wikilink 引用**
```bash
# 查找其他文件对目标 L2/L3 的引用
rg --type md "\[\[{文件名不含扩展名}\]\]" \
  {主题目录}/ \
  0101-wiki-topics/ \
  0102-wiki-concepts/ \
  0103-wiki-entities/ \
  0104-wiki-comparisons/
```

**配置影响**
- `topics.yaml`: 该 topic 是否还有其他 L2 文件
- `tag-vocabulary.yaml`: tags 是否仅此 L2 使用
- `0101-wiki-topics/`: 主题综述页是否需要归档

#### 1.4 生成删除报告

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
删除影响范围报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【L2 文件】
路径: {topic}/{filename}.md
标题: {title}
ID: {id}
创建: {created}
主题: {topic}

【派生的 L3 文件】({count} 个)
- 0102-wiki-concepts/{path1}.md
- 0103-wiki-entities/{path2}.md
- ...

【关联资源】({count} 个)
- 0001-resource/{topic}/{image1}.png (独占)
- 0001-resource/{topic}/{image2}.jpg (共享，保留)

【配置影响】
- topics.yaml: {topic} 将从 active 移除/保留
- tag-vocabulary.yaml: {count} 个 tag 可能标记为 unused

【死链风险】({count} 处)
- {file1}: 引用 [[{target}]]
- {file2}: 引用 [[{target}]]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 2: 用户确认

**强制确认点** — 必须用户明确同意才能继续

询问用户：
```
即将删除以下内容：
1. L2 文件: {path}
2. 派生 L3 文件: {count} 个
3. 独占资源文件: {count} 个
4. 数据库索引记录

删除的文件将移入 .trash/ 目录，可在需要时恢复。

❗ 注意: 
- 将产生 {count} 处死链
- {topic} 主题将 {影响描述}

是否继续删除？(y/N)
```

用户必须输入 `y` 或 `yes` 才能继续。

### Phase 3: 执行删除

#### 3.1 创建备份批次

```bash
# 生成带时间戳的批次ID
BATCH_ID=$(date +%Y%m%d_%H%M%S)
TRASH_DIR=".trash/remove-l2-${BATCH_ID}"

# 创建分类目录
mkdir -p "$TRASH_DIR"/{l2,l3,resources,logs}

# 保存删除清单
cat > "$TRASH_DIR/manifest.txt" <<EOF
batch_id: ${BATCH_ID}
timestamp: $(date -Iseconds)
l2_file: {L2文件路径}
l3_count: {count}
resource_count: {count}
EOF
```

#### 3.2 移动文件

**移动 L2 文件**
```bash
mv "{L2完整路径}" "$TRASH_DIR/l2/"
```

**移动派生的 L3 文件**
```bash
# 对每个 L3 文件
for l3 in {L3文件列表}; do
  mv "$l3" "$TRASH_DIR/l3/"
  echo "✓ 移动 L3: $(basename $l3)"
done
```

**移动独占资源**
```bash
# 仅移动不被其他文件引用的资源
for res in {独占资源列表}; do
  mv "0001-resource/$res" "$TRASH_DIR/resources/"
  echo "✓ 移动资源: $res"
done
```

#### 3.3 处理死链

**扫描死链**
```bash
# 查找引用已删除文件的 wikilink
for deleted in {已删除的L2和L3文件名列表}; do
  rg --type md "\[\[$deleted\]\]" \
    {主题目录}/ \
    0101-wiki-topics/ \
    0102-wiki-concepts/ \
    0103-wiki-entities/ \
    0104-wiki-comparisons/
done
```

**修复策略选择**

向用户展示死链列表，询问修复策略：

```
发现 {count} 处死链，请选择处理方式：

A. 移除死链 — 直接删除 [[link]] 标记
B. 标记断裂 — 改为 ~~[[link]]~~ (删除线)
C. 记录待建 — 加入引用文件的 planned_links

建议: [基于上下文给出推荐]

请选择 (A/B/C):
```

**应用修复**
根据用户选择批量处理所有死链。

#### 3.4 清理配置文件

**topics.yaml**

```python
# 检查该 topic 下是否还有其他 L2 文件
remaining_l2 = glob(f"{topic}/*.md")

if len(remaining_l2) == 0:
    # 从 active 移到 archived
    topics['domains'][domain]['active'].remove(topic)
    topics['domains'][domain]['archived'].append({
        'name': topic,
        'archived_date': today(),
        'reason': f'最后一个 L2 文件已删除 (batch: {BATCH_ID})'
    })
```

**tag-vocabulary.yaml**

```python
# 检查每个 tag 是否还有其他文件使用
for tag in deleted_tags:
    usages = rg(f"tags:.*{tag}")
    if len(usages) == 0:
        tag_vocab[tag]['status'] = 'unused'
        tag_vocab[tag]['last_used'] = today()
```

**0101-wiki-topics/**

```bash
# 如果该 topic 不再有 L2 文件，归档主题综述页
if [ -z "$(ls {topic}/*.md 2>/dev/null)" ]; then
  topic_overview="0101-wiki-topics/{topic显示名}.md"
  if [ -f "$topic_overview" ]; then
    mv "$topic_overview" "$TRASH_DIR/logs/"
    echo "✓ 归档主题综述: $topic_overview"
  fi
fi
```

#### 3.5 更新数据库索引

如果存在 `.wiki.db` 索引：

```python
# 从索引中移除记录
import sqlite3

conn = sqlite3.connect('.wiki.db')
cursor = conn.cursor()

all_removed = [l2_path] + l3_paths

for path in all_removed:
    cursor.execute("DELETE FROM files WHERE path = ?", (path,))
    print(f"✓ 从索引移除: {path}")

conn.commit()
conn.close()
```

### Phase 4: 验证与日志

#### 4.1 运行配置同步检查

```bash
python 0100-wiki-meta/scripts/check-config-sync.py
```

确保所有检查项通过：
- ✅ topics.yaml 没有指向已删除文件的引用
- ✅ 数据库索引已同步
- ✅ 死链已按策略处理
- ✅ 资源引用一致性

如果检查失败，必须修复后才能继续。

#### 4.2 生成操作日志

在 `0109-log/remove-l2-{BATCH_ID}.md` 创建详细日志：

```markdown
---
operation: remove-l2
batch_id: {BATCH_ID}
timestamp: 2026-07-08T01:16:58+08:00
operator: Claude
status: completed
---

# L2 删除操作日志

## 删除的 L2 文件

- **路径**: {L2文件路径}
- **标题**: {title}
- **主题**: {topic}
- **创建时间**: {created}
- **删除原因**: {用户提供的原因}

## 清理的派生数据

### L3 文件 ({count} 个)

| 类型 | 路径 | 标题 |
|------|------|------|
| concept | 0102-wiki-concepts/{path} | {title} |
| entity | 0103-wiki-entities/{path} | {title} |

### 资源文件 ({count} 个)

- 0001-resource/{topic}/{file1}.png (独占，已删除)
- 0001-resource/{topic}/{file2}.jpg (共享，已保留)

## 配置变更

### topics.yaml
- {topic}: {从 active 移除 / 保持不变}

### tag-vocabulary.yaml
- {tag1}: 标记为 unused
- {tag2}: 仍被其他文件使用

### 0101-wiki-topics/
- {topic显示名}.md: {归档 / 保持不变}

## 死链处理

- **策略**: {移除死链 / 标记断裂 / 记录待建}
- **影响文件数**: {count}
- **详细列表**:
  - {file1}: 已修复
  - {file2}: 已修复

## 数据库变更

- **移除记录数**: {count}
- **同步状态**: PASS

## 备份位置

所有删除的文件已移入: `.trash/remove-l2-{BATCH_ID}/`

### 备份清单
```
.trash/remove-l2-{BATCH_ID}/
├── l2/
│   └── {L2文件名}.md
├── l3/
│   ├── {L3文件1}.md
│   └── {L3文件2}.md
├── resources/
│   ├── {资源1}.png
│   └── {资源2}.jpg
└── manifest.txt
```

## 恢复方式

如需恢复，按以下步骤：

1. 检查备份完整性
```bash
ls -lR .trash/remove-l2-{BATCH_ID}/
```

2. 手动恢复文件到原位置
3. 重建数据库索引
```bash
python 0100-wiki-meta/scripts/rebuild-index.py
```

4. 恢复配置项（参考上方"配置变更"反向操作）

## 验收清单

- [x] L2 文件已移入 .trash/
- [x] 派生 L3 文件已清理
- [x] 独占资源已移入 .trash/
- [x] 数据库索引已更新
- [x] 死链已处理
- [x] 配置文件已同步
- [x] check-config-sync.py 通过
- [x] 操作日志已生成
```

#### 4.3 Git 提交（可选）

如果用户要求提交到 Git，使用以下格式：

```bash
git status
git add .
git commit -m "wiki: remove L2 {title} — 清理 {L3 count} 个派生文件

- 移除 L2: {topic}/{filename}.md
- 清理 L3: {count} 个 concept/entity/comparison
- 清理资源: {count} 个独占文件
- 备份位置: .trash/remove-l2-{BATCH_ID}/
- 死链处理: {策略描述}
- 原因: {删除原因简述}

Batch: {BATCH_ID}"
```

**重要提醒**：
- ✅ `git commit` 可以执行
- ❌ `git push` **必须单独交用户确认，禁止自行推送**

---

## 边界情况处理

### 1. L3 引用多个 L2 源

**场景**: L3 的 `source` 字段包含多个 L2 路径

```yaml
source: 
  - "3000-Agent/agent-loop.md"
  - "3001-RAG/retrieval-basics.md"  # 要删除的
```

**处理策略**:
- 从该 L3 的 `source` 列表移除被删除的 L2
- **不删除** L3 文件本身
- 在 L3 正文中添加标注：

```markdown
> ⚠️ 注意: 本文部分内容源自已删除的 L2 文件 `3001-RAG/retrieval-basics.md` (删除于 2026-07-08)
```

### 2. 资源被多个文件共享

**场景**: 一个图片被多个 L2/L3 引用

**检测方法**:
```bash
# 查找资源的所有引用
rg --type md "0001-resource/{topic}/{filename}" \
  {所有主题目录}/ \
  0102-wiki-concepts/ \
  0103-wiki-entities/ \
  0104-wiki-comparisons/
```

**处理策略**:
- 引用数 = 1 → 移入 .trash/（独占）
- 引用数 > 1 → 保留，仅从当前 L2 的 `resource_refs` 移除

### 3. Topic 的最后一个 L2

**场景**: 删除后该 topic 目录为空

**处理策略**:
- topics.yaml: 从 `active` 移到 `archived`
- 0101-wiki-topics/: 归档主题综述页到 .trash/
- **保留** topic 目录结构（可能将来还会有新内容）
- 在 LOG 中标记为"topic 归档"

### 4. 删除操作中断

**场景**: 操作执行到一半时出错或用户中止

**恢复机制**:
- .trash/ 中的 `manifest.txt` 记录了计划删除的文件清单
- 检查清单与实际状态的差异
- 提供两个选项：
  - `--resume`: 继续未完成的删除
  - `--rollback`: 恢复已删除的部分

**实现**:
```bash
# 检查中断状态
python 0100-wiki-meta/scripts/check-remove-status.py \
  --batch-id {BATCH_ID}

# 继续删除
python 0100-wiki-meta/scripts/resume-remove.py \
  --batch-id {BATCH_ID}

# 或回滚
python 0100-wiki-meta/scripts/rollback-remove.py \
  --batch-id {BATCH_ID}
```

### 5. 级联删除风险

**场景**: 删除的 L3 被其他文件大量引用

**保护措施**:
- 在 Phase 1 分析阶段统计 wikilink 引用数
- 如果某个 L3 被引用 > 10 次，**额外警告**：

```
⚠️  高风险删除警告

L3 文件 [{L3文件名}] 被 {count} 个文件引用。
删除将产生大量死链，可能影响知识图谱完整性。

建议: 考虑使用 Update 操作修改内容，而非删除。

仍要继续删除吗？(y/N)
```

---

## 安全检查清单

删除操作开始前，必须通过以下检查：

- [ ] 用户已明确确认删除操作
- [ ] 影响范围报告已完整展示
- [ ] .trash/ 目录存在且可写
- [ ] .trash/ 目录空间充足（至少 100MB 可用）
- [ ] 当前工作目录干净（无未提交修改，避免混淆）
- [ ] 关键配置文件有最近备份
- [ ] 数据库文件（如存在）可读写
- [ ] 没有其他 Claude 实例正在操作同一仓库

**如果任一项不满足，终止操作并提示用户。**

---

## 与其他操作的关系

### Ingest ↔ Remove

- **Remove 是 Ingest 的反向操作**
- Ingest 创建 L2 → L3 → 资源 → 配置
- Remove 删除 配置 → 资源 → L3 → L2
- 顺序相反，确保依赖关系正确清理

### Update vs Remove

**何时使用 Update**:
- 修正错误内容
- 更新过时信息
- 调整标签和分类

**何时使用 Remove**:
- 内容重复（与其他 L2 重叠）
- 内容质量低且无法修复
- 来源不可靠且已有替代
- 主题不再相关

**重构场景**:
如果需要重大重构（如拆分或合并 L2）：
1. Remove 旧 L2
2. 重新 Ingest 新内容
3. 手动建立 wikilink 连接

### Lint 配合

删除操作后应立即运行 Lint：
```bash
# 删除完成后
python 0100-wiki-meta/scripts/skill-lint.md

# 检查项目：
# - 死链是否完全清理
# - 配置文件一致性
# - 孤立页面（如果有新产生）
# - 资源引用完整性
```

### Query 影响

- 删除后，相关查询将返回空结果
- 如果删除的是高频查询的概念，考虑创建重定向或别名
- 在主题综述页添加"已归档概念"章节

---

## 快速参考

### 典型删除流程

```bash
# 1. 用户在对话中 @ 引用需要删除的 L2 文件
# 2. Claude 读取文件并追溯派生关系
# 3. 生成影响范围报告
# 4. 用户确认
# 5. 执行删除（移入 .trash/）
# 6. 清理配置和数据库
# 7. 生成日志
# 8. (可选) Git 提交
```

### 恢复已删除的内容

```bash
# 1. 查看可恢复的批次
ls -lt .trash/remove-l2-*/

# 2. 检查特定批次的内容
cat .trash/remove-l2-20260708_011658/manifest.txt

# 3. 手动恢复文件
# 从 .trash/remove-l2-{BATCH_ID}/ 复制回原位置

# 4. 重建索引
python 0100-wiki-meta/scripts/rebuild-index.py

# 5. 恢复配置项
# 根据 LOG 文件中的"配置变更"章节反向操作
```

### 批量删除建议

如需删除多个相关的 L2 文件：

**推荐方式**: 逐个执行，每次验证
```
删除 L2-A → 验证 → 删除 L2-B → 验证 → ...
```

**不推荐**: 一次性批量删除
- 风险: 难以追踪影响范围
- 恢复: 批量恢复复杂度高
- 验证: 难以定位具体问题

---

## 注意事项

### 1. 不可逆性

虽然删除的文件移入 `.trash/`，但一旦执行 `git push`：
- 删除操作传播到远程仓库
- 团队其他成员拉取后也会丢失这些文件
- 恢复需要协调所有成员

**建议**: 删除敏感或重要内容时，先在本地验证几天再推送。

### 2. 依赖检查的重要性

删除前必须充分检查依赖关系：
- ❌ 跳过依赖检查 → 破坏知识图谱完整性
- ✅ 完整分析 → 安全清理，保持一致性

**特别注意**:
- 跨主题引用（如 Agent 概念引用 RAG 概念）
- 基础概念被高级概念引用
- 实体被多个 concept 引用

### 3. 定期清理 .trash/

.trash/ 目录会随着删除操作累积：
- 建议每 30 天清理一次超过 30 天的批次
- 清理前确认无需恢复
- 可设置自动化任务：

```bash
# 清理 30 天前的删除批次
find .trash/remove-l2-* -type d -mtime +30 -exec rm -rf {} \;
```

### 4. 数据库索引同步

删除操作后数据库索引必须同步：
- check-config-sync.py 会验证索引一致性
- 如果索引损坏，运行 rebuild-index.py 重建
- 定期备份 .wiki.db

### 5. 团队协作注意

多人协作场景下：
- 删除前在团队频道通知
- 给出 review 期限（如 3 天）
- 删除重要概念需团队共识
- 记录删除原因（便于将来质疑时解释）

---

## 支持脚本需求

Remove 操作需要以下辅助脚本（待创建）：

### check-remove-status.py
检查删除操作的完成状态，识别中断的批次。

### resume-remove.py
继续未完成的删除操作。

### rollback-remove.py
回滚部分执行的删除操作。

### rebuild-index.py
重建数据库索引（删除后同步）。

### clean-old-trash.py
定期清理超过指定天数的 .trash/ 内容。

---

## 总结

Remove 操作是 Mnemosyne 系统的"手术刀"，使用时需要：

✅ **DO**:
- 详细分析影响范围
- 展示完整报告给用户
- 保留备份到 .trash/
- 记录详细日志
- 验证配置同步
- 处理所有死链

❌ **DON'T**:
- 跳过用户确认
- 直接删除文件（不备份）
- 忽略依赖关系
- 遗留配置残留
- 批量删除未验证
- 自行执行 git push

**原则**: 安全第一，可追溯，可恢复。
