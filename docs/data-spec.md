# 数据规范

## 1. 文档主键

每份资料分配稳定文档 ID：

- 格式：`mao-book-0001`、`mao-record-0001`
- 不直接用中文长文件名当主键
- 原始文件名保留在元数据中

## 2. 文件归档建议

### 原始文件
- 书籍 PDF：`data/raw/books/`
- 其他资料：`data/raw/other/`

### 转换输出
- 原始 Markdown：`data/markdown/{doc_id}.md`
- 清洗 Markdown：`data/clean/{doc_id}.md`
- 元数据：`data/metadata/{doc_id}.json`
- 索引切片：`data/index/{doc_id}.json`

## 3. 元数据字段

建议每份文档至少包含：

- `doc_id`
- `title`
- `subtitle`
- `creator`
- `editor`
- `document_type`：book / letter / speech / article / memoir / chronology / archive / other
- `source`
- `source_detail`
- `publication_date`
- `original_date`
- `volume`
- `edition`
- `language`
- `is_scanned_pdf`
- `has_ocr`
- `page_start`
- `page_end`
- `tags`
- `notes`

## 4. Markdown 清洗原则

- 保留文义，不随意改写原文
- 删除明显页眉页脚、页码噪音、扫描残留脏字符
- 修复明显断行与错误分段
- 章节标题统一层级
- 表格、脚注、引用尽量保留结构
- 所有重大人工改动要可回溯

## 5. 面向后续知识整理的补充字段

后续在结构化阶段补充：

- `persons`
- `organizations`
- `events`
- `places`
- `works`
- `concepts`
- `time_expressions`
- `references`
- `related_doc_ids`

## 6. Phase 2 结构化抽取目录结构

在 `data/index/` 下组织结构化抽取结果：

```
data/index/
├── articles/           # 文章切分结果
│   ├── mao-volume-01.articles.jsonl
│   ├── mao-volume-02.articles.jsonl
│   └── ...
├── entities/           # 实体抽取结果
│   ├── persons.jsonl
│   ├── events.jsonl
│   ├── organizations.jsonl
│   ├── places.jsonl
│   ├── works.jsonl
│   ├── concepts.jsonl
│   └── time_expressions.jsonl
├── relations/          # 关系抽取结果
│   └── relations.jsonl
└── archives/           # 档案聚合结果
    ├── person_archives/
    │   ├── person-mao-zedong.json
    │   └── ...
    ├── event_archives/
    ├── organization_archives/
    ├── place_archives/
    └── work_archives/
```

### 格式说明

- **JSONL 格式**：用于实体、关系、文章列表
  - 每行一个 JSON 对象
  - 便于流式处理和增量更新
  - 示例：`{"entity_id": "person-001", "name": "毛泽东", ...}\n`

- **JSON 格式**：用于档案文件
  - 每个档案一个独立文件
  - 便于单独查看和更新
  - 文件名：`{entity_id}.json`

### 数据流向

```
cleaned markdown (data/clean/volumes/)
    ↓
文章切分 (data/index/articles/)
    ↓
实体抽取 (data/index/entities/)
    ↓
关系抽取 (data/index/relations/)
    ↓
档案生成 (data/index/archives/)
```

## 7. 版本原则

- 原始 PDF 不覆盖
- 原始 Markdown 不覆盖
- 清洗后 Markdown 独立保存
- 结构化输出独立保存
- 每次抽取保留时间戳，支持增量更新
