- **D003**: L2统一kind:standard，不区分concept/entity/comparison。
- **D004**: topic/concept/entity/comparison属L3加工形态。
- **D013**: L3按概念/实体/对比独立建页；0101为域级主题综述。
- **D015**: entity按entity_type归档；comparison按comparison_axis归档；concept按主题域。
- **D016**: L2必须含原文主体，不允许过度摘要化。

### 字段
- **D006**: L3使用processing_path。
- **D012**: source保持单一字段。
- **D014**: L3 source为文件级L2路径列表。
- **D019**: L2 id=SHA256(topic+slug+created)[:8]；content_hash=SHA256(全文)[:8]。

### 操作
- **D008**: L1标准化后移入.trash/，用户确认后执行。
- **D009**: slug英文优先，3-5推荐选项。
- **D010**: L3不允许人工编辑内容逻辑。
- **D011**: tags词表收敛到tag-vocabulary.yaml。
- **D017**: 正式wikilink仅链接已存在页面；未建概念入planned_links。
- **D018**: 文件名空格→-，主体.→_；title保留原始标题。

## 待验证
- 正式Ingest（entity/comparison主动触发效果）
- 图片下载→本地→引用全链路
- 多来源级联合并 / Lint完整流程 / 跨主题引用效果
