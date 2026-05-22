# 决策记录

> 状态：当前决策索引
> 更新时间：2026-05-20

## D001 三层架构收束

- 决策：采用 L1 原始数据层、L2 主题知识层、L3 知识加工层。
- 原因：把原始保存、标准化沉淀、知识加工拆开，降低 Claude 写入时混层的风险。
- 影响：写入固定为 L1 → L2 → L3，查询固定为 L3 → L2 → L1。

## D002 L1 可删除或归档

- 决策：L1 是临时原始数据层，完成 L2 标准化后不再作为主数据源。
- 原因：避免原始素材长期干扰检索；同时允许按需追溯。
- 影响：Ingest 完成后询问删除或归档 L1。

## D003 L2 只保存标准化主题知识

- 决策：L2 不再区分 concept/entity/topic/comparison，只使用 `kind: standard`。
- 原因：L2 是 L1 的标准化数据，不承担知识拆解和重构。
- 影响：L2 统一使用 `t-knowledge.md`。

## D004 L3 承担知识加工

- 决策：topic/concept/entity/comparison 属于 L3 加工页面形态。
- 原因：这些页面需要基于多个 L2 条目拆解、重构、聚合。
- 影响：L3 使用 `s-topic.md`、`s-concept.md`、`s-entity.md`、`s-comparison.md`。

## D005 删除单条数字 ID

- 决策：单条知识不维护数字 ID。
- 原因：当前没有外部系统依赖稳定 ID，数字 ID 增加维护成本。
- 影响：使用“主题目录路径 + slug 文件名”定位知识。

## D006 字段命名使用 processing_path

- 决策：L3 页面使用 `processing_path` 表示加工路径。
- 原因：避免 `synthesis_path` 继续暗示旧的“合成层”模型。
- 影响：模板和 Query 均使用 `processing_path`。

## D007 文档治理策略

- 决策：`CURRENT.md` 是当前唯一方案入口，历史 phase 文档保留。
- 原因：项目仍在设计开发中，需要保留推演过程，但不能让旧口径变成执行依据。
- 影响：后续 Claude 或人工阅读应先看 `CURRENT.md`。

## D008 L1 默认移入回收站

- 决策：Ingest 完成后默认将 L1 原文件移入 `0003-inbox/.trash/` 回收站，执行前需用户确认。
- 原因：L1 是临时层，完成 L2 标准化后不再作为主数据源；回收站语义比“删除”更准确，同时保留确认机会防止误操作。
- 影响：Ingest 完成后默认建议移入 `.trash/`，经用户确认后执行，非永久删除。

## D009 slug 英文优先 + 推荐选项

- 决策：L2 slug 优先用英文生成；操作时 Claude 给出 3-5 个推荐选项，用户确认或手动指定。
- 原因：英文 slug 在 wikilink 中更短、跨平台兼容更好；推荐选项机制保留用户最终决定权。
- 影响：Ingest 步骤中新增"生成 3-5 个 slug 推荐选项"环节。

## D010 L3 不允许人工直接编辑内容逻辑

- 决策：L3 加工页面由 Claude 维护，不允许人工直接编辑内容逻辑。
- 原因：L3 是加工产出层，人工改动逻辑内容可能破坏跨页面连接和引用逻辑。
- 影响：仅允许错别字、格式等微调，不得改变 wikilink 连接和内容结构；逻辑修改应回到 L2 驱动更新。

## D011 tags 词表 P0 即收敛

- 决策：tags 在 P0 即建立受控词表，不延后到 P3。
- 原因：推迟治理会导致前期积累大量自由标签，后期清洗成本远高于从一开始约束。
- 影响：`tag-vocabulary.yaml` 为标签词表；`topics.yaml` 中预定义各主题域的推荐标签集。

## D012 source 保持单一字段

- 决策：`source` 不拆分为 `source_type` / `source_ref`，保持单一枚举字段。
- 原因：当前场景简单（manual / url / file / claude），拆分增加 Schema 复杂度但收益不大。
- 影响：`source` 字段枚举保持为 `manual | url | file | claude`。

## D013 L3 页面从域级聚合改为概念级独立页面

- 决策：L3 按概念/实体/对比独立建页，采用 `010{1-4}/大类/主题域/{slug}.md` 层级；0101 主题综述为域级 `大类/主题域.md`。
- 原因：域级聚合导致不同概念挤在同一文件，失去知识加工意义；独立页面支持深度展开，对齐 karpathy-llm-wiki 编译模式。
- 影响：细化 D004；Ingest 不再 4 目录全建，改为按需建单个概念页；移除 50 条硬分页；检索改为 topic 优先。

## D014 L3 使用 `source` 字段溯源 L2

- 决策：L3 的 `source` 字段改为列出具体的 L2 源文件路径（如 `[3001-深度学习/transformer.md]`），替代原来的 `source_topics`（仅到目录级）。
- 原因：L3 是 L2 的知识合成品，需要从 L3 追溯到具体的 L2 来源，而非只知道"來自某个主题目录"。
- 影响：全部 L3 模板和 Schema 中 `source_topics` 替换为 `source`，值为文件路径列表。

## D015 L3 entity/comparison 按各自维度归档

- 决策：entity 按 `entity_type`（Organization/Product/Project/Paper/Person）归档；comparison 按 `comparison_axis`（Architecture/Execution/Retrieval 等）归档；concept 保持按主题域归档。
- 原因：entity 和 comparison 天然跨主题，硬塞进 topic 目录导致重复建档和归属任意。
- 影响：0103/0104 目录结构变更为 `{entity_type}/{slug}.md` 和 `{comparison_axis}/{slug}.md`；entity 增 `entity_type` 字段；comparison 增 `comparison_axis`/`lhs`/`rhs` 字段。

## D016 L2 高保真标准化

- 决策：L2 是高保真标准化层（source of truth），默认保留原文主体，不允许过度摘要化。
- 原因：L3 由 L2 派生，若 L2 过度摘要则 L3 失去事实根基。
- 影响：L2 默认中文化；英文原文保留需用户确认；新增 `resource_refs` 字段；来源区保留作者/机构/链接。

## D017 死链治理

- 决策：正式 `[[wikilink]]` 只链接已存在页面；未建概念放入 `planned_links` 或 `<!-- TODO: -->` 注释。
- 原因：死链破坏 Obsidian Graph 和用户浏览体验；待建概念混入正式链接导致不可区分。
- 影响：skill-ingest/lint 新增死链检查；落盘验收清单包含死链项。

## D018 L2 命名规则：空格转 `-`，主体 `.` 转 `_`

- 决策：文件名禁止空格（转 `-`）；文件名主体中的 `.` 转 `_`（仅最后一个 `.` 是扩展名）；L2 `title` 保留原始标题，slug 仅用于路径定位。
- 原因：空格和多余 `.` 在命令行和 wikilink 中产生歧义；slug 不应替代标题语义。
- 影响：skill-ingest §2 增加命名规则；lint 增加 `filename_format` 检查。

## D019 L2 使用身份 hash 作为 ID + 内容 hash 作为完整性指纹

- 决策：L2 `id` = SHA256(topic + slug + created[:10])[:8]，身份不变则 ID 不变；`content_hash` = SHA256(文件全文)[:8]，内容变化时自动变化。
- 原因：稳定 ID 便于外部引用和扩展；content_hash 提供内容完整性校验能力。
- 影响：schema.yaml L2 新增 `id`(必填) 和 `content_hash`(可选)；skill-ingest §4 增加 hash 生成步骤。
