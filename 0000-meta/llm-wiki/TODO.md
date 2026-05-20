# 待办事项

> 状态：P0/P1 已完成，待实际操作验证
> 更新时间：2026-05-20

## P0 方案落地前 ✅

- [x] 基于 `CURRENT.md` 生成根目录 `CLAUDE.md`
- [x] 创建 `0000-meta/0001-templates/t-knowledge.md`
- [x] 创建 `0000-meta/0001-templates/t-inbox.md`
- [x] 创建 `0000-meta/0001-templates/s-topic.md`
- [x] 创建 `0000-meta/0001-templates/s-concept.md`
- [x] 创建 `0000-meta/0001-templates/s-entity.md`
- [x] 创建 `0000-meta/0001-templates/s-comparison.md`
- [x] 创建 `0000-meta/0003-configs/schema.yaml`
- [x] 创建 `0000-meta/0003-configs/topics.yaml`
- [x] 创建 `0000-meta/0003-configs/lint-rules.yaml`

## P0 目录与基础文件 ✅

- [x] 创建 L1/L2/L3 目录骨架
- [x] 创建 `0100-wiki-meta/INDEX.md`
- [x] 创建 `0100-wiki-meta/SCHEMA.md`
- [x] 创建 `0100-wiki-meta/RELATIONS.md`
- [x] 创建 `0109-log/`

## P1 Claude 工作流 ✅

- [x] 编写 `skill-ingest.md`
- [x] 编写 `skill-query.md`
- [x] 编写 `skill-update.md`
- [x] 编写 `skill-lint.md`
- [x] 编写 `skill-final-check.md`

## 待确认（已裁决 2026-05-20）

- [x] L1 默认删除 → D008：Ingest 完成后默认删除 L1 原文件，操作时确认归属
- [x] L2 slug 生成规则 → D009：英文优先，操作时给出 3-5 个推荐选项供确认
- [x] L3 加工页面是否允许人工直接编辑 → D010：不允许人工直接编辑，最多小幅修改且不影响连接和逻辑
- [x] `tags` 是否现在就收敛词表 → D011：现在就收敛，P0 即建立 tags 词表
- [x] `source` 是否需要拆成 `source_type` / `source_ref` → D012：保持单一 `source` 字段
