# Mnemosyne 用户指南

智能本地Wiki系统操作手册。

## 快速开始

### 初始化数据库

```bash
# 创建SQLite数据库和索引
python 0100-wiki-meta/scripts/init-db.py
python 0100-wiki-meta/scripts/index-notes.py
```

### 摄入新笔记

```bash
# 将原始笔记放入inbox
cp your-note.md 0003-inbox/

# 在Claude Code中引用文件触发摄入
# @0003-inbox/your-note.md
```

### 健康检查

```bash
# 运行完整的Lint检查
bash 0100-wiki-meta/scripts/run-lint.sh
```

## 常用操作

### 查询操作

```bash
# 查找死链
python 0100-wiki-meta/scripts/query.py --dead-links

# 数据库健康检查
python 0100-wiki-meta/scripts/check-db-health.py
```

### 批量操作

```bash
# 批量添加标签（预览）
python 0100-wiki-meta/scripts/batch-ops.py add-tags \
  --pattern "3000-*/*.md" --tags "agent,workflow" --dry-run

# 批量设置状态
python 0100-wiki-meta/scripts/batch-ops.py set-status \
  --pattern "0102-*/*.md" --status published

# 批量移动到回收站
python 0100-wiki-meta/scripts/batch-ops.py move-trash \
  --pattern "0003-inbox/*.md"
```

### 图谱分析

```bash
# 分析知识图谱拓扑
python 0100-wiki-meta/scripts/analyze-graph.py
```

### 修复死链

```bash
# 自动修复图片死链（预览）
python 0100-wiki-meta/scripts/fix-dead-image-links.py --dry-run

# 执行修复
python 0100-wiki-meta/scripts/fix-dead-image-links.py
```

## 目录结构

| 目录 | 用途 |
|------|------|
| `0003-inbox/` | L1原始数据（待摄入） |
| `3000-*/, 3001-*/` | L2主题知识层（source of truth） |
| `0102-wiki-concepts/` | L3概念知识 |
| `0103-wiki-entities/` | L3实体知识 |
| `0104-wiki-comparisons/` | L3对比分析 |
| `0101-wiki-topics/` | 主题域综述 |
| `0001-resource/` | 本地资源（图片/附件） |
| `.trash/` | 回收站 |

## 核心概念

- **L1**: 未加工原始素材
- **L2**: 高保真标准化数据（唯一事实源）
- **L3**: L2派生的typed wiki（按知识域组织）

详见 `CLAUDE.md` 完整规格。
