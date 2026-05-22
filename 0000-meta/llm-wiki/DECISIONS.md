# 决策记录

> 状态：当前决策索引 | 更新时间：2026-05-22

## 架构

- **D001**：L1 原始 → L2 高保真标准化 → L3 typed wiki。写入 L1→L2→L3，查询 L3→L2→L1。
- **D003**：L2 统一 `kind: standard`，不区分 concept/entity/topic/comparison。
- **D004**：topic/concept/entity/comparison 属于 L3 加工页面形态，L2 不承担此职责。
- **D013**：L3 按概念/实体/对比独立建页（`010{2-4}/维度/{slug}.md`），0101 为域级主题综述。
- **D015**：entity 按 `entity_type` 归档；comparison 按 `comparison_axis` 归档；concept 按主题域归档。
- **D016**：L2 是高保真 source of truth，必须含原文主体，不允许过度摘要化。

## 字段

- **D006**：L3 使用 `processing_path`。
- **D012**：`source` 保持单一字段，不拆分。
- **D014**：L3 `source` 为文件级 L2 路径列表（非目录级）。
- **D019**：L2 `id` = SHA256(topic+slug+created)[:8]；`content_hash` = SHA256(全文)[:8]。

## 操作

- **D008**：L1 标准化后移入 `.trash/`，用户确认后执行。
- **D009**：slug 英文优先，3-5 推荐选项，用户确认。
- **D010**：L3 不允许人工编辑内容逻辑，仅允许错别字或格式微调。
- **D011**：tags 词表 P0 收敛，写入 `tag-vocabulary.yaml`。
- **D017**：正式 [[wikilink]] 只链接已存在页面；未建概念入 `planned_links` 或注释。
- **D018**：文件名空格→`-`，主体 `.`→`_`；title 保留原始标题，slug 仅用于路径。
