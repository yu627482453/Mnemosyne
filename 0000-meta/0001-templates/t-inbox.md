---
title: "{{title}}"
date: "{{tp.file.creation_date("YYYY-MM-DD")}}"
source: "{{source}}"
source_url: "{{url}}"
status: raw
---

# {{title}}

## 原始内容

<!-- 保留原始内容，不做修改 -->

## 来源信息

- 来源：{{source}}
- URL：{{url}}
- 采集日期：{{tp.file.creation_date("YYYY-MM-DD")}}

## 处理状态

- [ ] 待 Claude 处理
