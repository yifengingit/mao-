# 数据清单

## 哪些数据在 Git 里

| 路径 | 大小 | 说明 |
|------|------|------|
| `data/clean/volumes/*.cleaned.md` | 5.4 MB | 清洗后的 7 卷 Markdown (核心源数据) |
| `data/metadata/` | 23 KB | QA 报告 + review 记录 |
| `data/index/articles/*.jsonl` | 220 KB | 421 篇文章切分结果 |
| `data/index/entities/*.deduplicated.jsonl` | ~1.8 MB | 去重后人物 + 地点 |
| `data/index/entities/places.jsonl` | 662 KB | 地点实体 (未去重) |
| `data/index/relations/*.jsonl` | 1.8 MB | 关系 (去重前 + 去重后) |
| `data/index/archives/` | 3.7 MB | 908 个实体档案 JSON |
| `data/index/graph/graph.json` | 1.4 MB | D3.js 可视化用图谱 |
| `data/index/graph/article_excerpts.json` | 467 KB | 文章摘要 |
| **总计** | **~15 MB** | |

## 哪些数据不在 Git 里 (.gitignore)

| 路径 | 大小 | 说明 | 如何重建 |
|------|------|------|---------|
| `data/raw/books/` | 26 MB | 原始 PDF (版权材料) | 需要用户提供 |
| `data/markdown/` | 3.8 MB | markitdown 原始输出 | `convert_volume.py` |
| `data/staging/` | 143 KB | 日志临时文件 | 脚本运行时自动生成 |
| `data/index/entities/persons.raw.jsonl` | 1.7 MB | 未去重人物实体 | `extract_entities.py` |
| `data/index/entities/persons.jsonl` | 1.4 MB | 后处理人物实体 | `extract_entities.py` |

## 各文件详细说明

### data/clean/volumes/ (清洗后 Markdown)

这是整个管线的基础输入。所有下游脚本都从这里读取。

| 文件 | 大小 | 文章数 |
|------|------|--------|
| mao-volume-01.cleaned.md | 638 KB | 18 篇 (1925-1927) |
| mao-volume-02.cleaned.md | 793 KB | 41 篇 (1927-1937) |
| mao-volume-03.cleaned.md | 574 KB | 37 篇 (1937-1941) |
| mao-volume-04.cleaned.md | 692 KB | 71 篇 (1941-1945) |
| mao-volume-05.cleaned.md | 820 KB | 80 篇 (1945-1949) |
| mao-volume-06.cleaned.md | 928 KB | 75 篇 (1949-1957) |
| mao-volume-07.cleaned.md | 1.1 MB | 99 篇 (1957-1985) |

### data/index/articles/*.articles.jsonl

每行一个文章对象:

```json
{
  "article_id": "mao-volume-01-article-001",
  "volume_id": "mao-volume-01",
  "title": "中国社会各阶级的分析",
  "date_raw": "一九二五年十二月一日",
  "date_iso": "1925-12-01",
  "content_lines": {"start": 15, "end": 89},
  "footnote_lines": {"start": 90, "end": 95},
  "word_count": 4521,
  "paragraph_count": 23
}
```

`content_lines.start/end` 是在对应 cleaned.md 中的行号 (1-based)，用于定位原文。

### data/index/entities/persons.deduplicated.jsonl

每行一个去重后的人物实体:

```json
{
  "name": "蒋介石",
  "aliases": ["蒋中正", "蒋"],
  "entity_type": "person",
  "attributes": {
    "roles": ["国民党领导人", "军事将领"],
    "affiliations": ["中国国民党", "国民政府"]
  },
  "mentions": [{"article_id": "...", "context": "...", "mention_index": 1}, ...],
  "confidence": 0.98,
  "source_article": "mao-volume-01-article-001",
  "merged_from": 114,
  "merged_articles": ["mao-volume-01-article-001", ...]
}
```

### data/index/relations/relations.deduplicated.jsonl

每行一个去重后的关系:

```json
{
  "relation_id": "rel-xxx",
  "from_entity_name": "毛泽东",
  "from_entity_type": "person",
  "to_entity_name": "蒋介石",
  "to_entity_type": "person",
  "relation_type": "opposed_to",
  "confidence": 0.95,
  "evidence": [
    {
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "context": "原文引用..."
    }
  ]
}
```

### data/index/archives/

每个实体一个 JSON 文件。由 `generate_archives.py` 聚合生成。
`index.json` 是所有档案的索引。

### data/index/graph/graph.json

D3.js 力导向图用的最终数据。结构见 architecture.md。

### data/index/graph/article_excerpts.json

```json
{
  "mao-volume-01-article-001": {
    "article_id": "mao-volume-01-article-001",
    "volume_id": "mao-volume-01",
    "title": "中国社会各阶级的分析",
    "date_iso": "1925-12-01",
    "excerpt": "前300字正文..."
  }
}
```
