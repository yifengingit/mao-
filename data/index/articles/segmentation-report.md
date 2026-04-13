# 文章切分统计报告

生成时间：2026-04-12

## 总体统计

- 总卷数：7 卷
- 总文章数：421 篇
- 平均每卷：60.1 篇

## 各卷详情

| 卷册 ID | 文章数 | 输出文件 |
|---------|--------|----------|
| mao-volume-01 | 18 | data/index/articles/mao-volume-01.articles.jsonl |
| mao-volume-02 | 41 | data/index/articles/mao-volume-02.articles.jsonl |
| mao-volume-03 | 37 | data/index/articles/mao-volume-03.articles.jsonl |
| mao-volume-04 | 71 | data/index/articles/mao-volume-04.articles.jsonl |
| mao-volume-05 | 80 | data/index/articles/mao-volume-05.articles.jsonl |
| mao-volume-06 | 75 | data/index/articles/mao-volume-06.articles.jsonl |
| mao-volume-07 | 99 | data/index/articles/mao-volume-07.articles.jsonl |

## 切分质量验证

### 抽样检查（mao-volume-01）

已验证第 1 卷的 18 篇文章：
- 标题识别：准确
- 日期解析：准确（中文日期 -> ISO 格式）
- 正文边界：准确
- 注释区域：准确识别

示例文章：
```json
{
  "article_id": "mao-volume-01-article-001",
  "title": "中国社会各阶级的分析",
  "date_iso": "1925-12-01",
  "word_count": 3410,
  "paragraph_count": 8
}
```

### 抽样检查（mao-volume-02）

已验证第 2 卷的前 3 篇文章：
- 标题识别：准确
- 日期解析：准确
- 正文边界：准确
- 注释区域：准确识别（包括无注释的文章）

示例文章：
```json
{
  "article_id": "mao-volume-02-article-003",
  "title": "反对自由主义",
  "date_iso": "1937-09-07",
  "has_title_note": false,
  "notes_lines": null
}
```

## 输出格式

每篇文章输出为一行 JSON，包含以下字段：

- `article_id`: 文章唯一标识符
- `volume_id`: 所属卷册 ID
- `title`: 文章标题
- `has_title_note`: 是否有题注
- `date_original`: 原始日期字符串
- `date_iso`: ISO 8601 格式日期
- `title_line`: 标题所在行号
- `date_line`: 日期所在行号
- `content_lines`: 正文行号范围 `{start, end}`
- `notes_lines`: 注释行号范围 `{start, end}` 或 `null`
- `word_count`: 字数统计
- `paragraph_count`: 段落数量

## 下一步

文章切分已完成，可进入 Phase 2 Stage 3：实体抽取实现。

建议先对少量文章（如 volume-01 的前 5 篇）进行实体抽取测试，验证 DeepSeek API 调用和 prompt 效果。
