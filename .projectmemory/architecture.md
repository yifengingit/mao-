# 架构 & 脚本依赖关系

## 数据管线依赖图

```
split_volumes.py
  需要: data/raw/books/毛泽东选集.pdf + data/metadata/volume_manifest.json
  产出: data/raw/books/volumes/mao-volume-0{1..7}.pdf

convert_volume.py
  需要: data/raw/books/volumes/mao-volume-XX.pdf
  产出: data/markdown/{engine}/mao-volume-XX/...

clean_markdown.py
  需要: data/markdown/markitdown/mao-volume-XX/...
  产出: data/clean/volumes/mao-volume-XX.cleaned.md

segment_articles.py
  需要: data/clean/volumes/mao-volume-XX.cleaned.md
  产出: data/index/articles/mao-volume-XX.articles.jsonl

extract_entities.py  ⚠️ 需要 DEEPSEEK_API_KEY 环境变量
  需要: data/index/articles/*.articles.jsonl + data/clean/volumes/*.cleaned.md
  产出: data/index/entities/persons.raw.jsonl, places.jsonl

deduplicate_entities.py
  需要: data/index/entities/persons.raw.jsonl (或 persons.jsonl)
  产出: data/index/entities/persons.deduplicated.jsonl

extract_relations.py  ⚠️ 需要 DEEPSEEK_API_KEY 环境变量
  需要: data/index/articles/*.articles.jsonl + data/index/entities/persons.deduplicated.jsonl
  产出: data/index/relations/relations.jsonl

deduplicate_relations.py
  需要: data/index/relations/relations.jsonl
  产出: data/index/relations/relations.deduplicated.jsonl

generate_archives.py
  需要: entities/*.deduplicated.jsonl + relations/*.deduplicated.jsonl + articles/*.jsonl
  产出: data/index/archives/ (585 + 323 个 JSON 文件) + index.json

build_graph.py
  需要: entities/*.deduplicated.jsonl + relations/*.deduplicated.jsonl + articles/*.jsonl
  产出: data/index/graph/graph.json
  依赖: networkx, python-louvain

build_article_excerpts.py
  需要: data/index/articles/*.jsonl + data/clean/volumes/*.cleaned.md
  产出: data/index/graph/article_excerpts.json

analyze_graph.py (可选, 仅输出统计)
  需要: data/index/graph/graph.json
```

## Python 依赖

```
# 核心依赖 (requirements.txt 不存在, 需要手动安装)
networkx          # 图谱构建
python-louvain    # 社群检测 (import community)
requests          # DeepSeek API 调用
# markitdown / marker  # PDF 转换 (Phase 1, 已完成)
```

## 可视化架构

`visualize/index.html` 是一个独立的单文件 HTML:
- 通过 CDN 加载 D3.js v7
- 通过 fetch 加载两个 JSON: `graph.json` + `article_excerpts.json`
- 所有逻辑在 `<script>` 标签内，无构建工具
- 需要一个静态文件服务器（因为 fetch 不支持 file:// 协议）

### 可视化核心状态

```javascript
let minDegree  = 5;      // 密度过滤: 5=精要, 3=扩展, 0=全量
let searchText = "";      // 搜索框
let currentYear = 9999;   // 时间轴: 9999=显示全部, 否则截至该年
let highlighted = null;   // 当前高亮节点 ID
let bioNode     = null;   // 传记模式的目标节点
let playTimer   = null;   // 播放定时器
```

### 可视化关键函数

- `main()` - 加载数据, 构建图谱, 隐藏 loading
- `buildGraph(excerpts)` - 创建 D3 force simulation, 绑定事件
- `getFilteredData()` - 按 minDegree/searchText/currentYear 过滤节点和边
- `zoomToFit(zoom, W, H, simNodes)` - 模拟结束后自动缩放适配
- `buildTimeline()` - 构建底部时间轴直方图 + 拖拽交互
- `setYear(y)` - 设置当前年份, 更新时间轴 UI + 过滤节点
- `showNodePanel(orig, excerpts, simNodes, simLinks)` - 右侧面板: 节点详情
- `showEdgePanel(l, excerpts)` - 右侧面板: 边详情
- `startBio(orig, simNodes, simLinks)` - 进入传记模式

## JSONL 格式约定

项目中大量使用 JSONL（每行一个 JSON 对象）。读取方式:

```python
def load_jsonl(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items
```

几乎每个脚本都有这个函数的副本。没有抽成公共模块。

## graph.json 数据结构

```json
{
  "nodes": [
    {
      "id": "毛泽东",
      "node_type": "person",          // person | place | organization
      "aliases": ["Chairman Mao"],
      "roles": ["革命家", "思想家"],
      "affiliations": ["中国共产党"],
      "mention_count": 323,
      "confidence": 0.98,
      "first_seen": "1925-12-01",     // 首次出现的文章日期
      "last_seen": "1985-01-01",      // 最后出现
      "degree": 173,                  // 无向度
      "degree_centrality": 0.162,
      "betweenness_centrality": 0.125,
      "betweenness_norm": 1.0,        // 归一化到 0-1, 用于节点大小
      "community_id": 0               // Louvain 社群 ID
    }
  ],
  "links": [
    {
      "source": "毛泽东",
      "target": "蒋介石",
      "relation_type": "opposed_to",
      "confidence": 0.95,
      "source_articles": ["mao-volume-01-article-001", ...],
      "relation_id": "rel-xxx",
      "first_date": "1926-03-01",     // 最早证据的文章日期
      "evidence_items": [             // 原文证据
        {
          "article_id": "mao-volume-01-article-001",
          "article_title": "中国社会各阶级的分析",
          "date_iso": "1926-03-01",
          "context": "原文摘录..."
        }
      ]
    }
  ],
  "meta": {
    "node_count": 1068,
    "link_count": 1091,
    "node_types": {"person": 589, "place": 323, "organization": 156},
    "communities": 479
  }
}
```

## 节点度分布 (决定密度切换阈值)

| 筛选条件 | 节点数 | 用途 |
|----------|--------|------|
| degree >= 5 | 99 | 精要模式 (默认) |
| degree >= 3 | 194 | 扩展模式 |
| degree >= 0 | 1,068 | 全量模式 |

## Top 10 节点 (按 degree)

1. 毛泽东: degree=173
2. 蒋介石: degree=105
3. 中国共产党: degree=39
4. 周恩来: degree=32
5. 孙中山: degree=28
6. 斯大林: degree=28
7. 延安: degree=26
8. 列宁: degree=23
9. 希特勒: degree=22
10. 马克思: degree=21
