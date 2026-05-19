# 决策记录

> 状态：当前决策索引
> 更新时间：2026-05-19

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
