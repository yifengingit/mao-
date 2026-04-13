# 毛泽东选集 · 知识图谱

从 PDF 到知识图谱的完整 NLP 管线。覆盖《毛泽东选集》全 7 卷 421 篇文章 (1919-1985)，提取 577 个人物、323 个地点、1,176 条关系，生成可交互的 D3.js 力导向图。

## 在线演示

```bash
git clone https://github.com/yifengingit/mao-.git
cd mao-
python -m http.server 8766
# 浏览器打开 http://localhost:8766/visualize/index.html
```

## 截图

默认视图展示 99 个核心节点 (degree >= 5)，GitHub 暗色主题，节点大小表示中心度 (betweenness centrality)，颜色表示社群 (Louvain community detection)。

功能包括:
- 三级密度切换: 精要 (99) / 扩展 (194) / 全量 (1,068)
- 时间轴滑块: 拖动 1919-1985，看网络随时间涌现
- 传记模式: 选中任意人物，播放其关系网络随年份积累
- 来源段落: 点击边查看原文证据引用
- 搜索: 实时过滤人物和地点

## 管线

```
PDF (7卷)
  → split_volumes.py → 7 个卷 PDF
  → convert_volume.py → Markdown
  → clean_markdown.py → 清洗 Markdown (5.4 MB)
  → segment_articles.py → 421 篇文章
  → extract_entities.py → 1,746 条实体 (DeepSeek API)
  → deduplicate_entities.py → 577 人物 + 323 地点
  → extract_relations.py → 1,451 条关系 (DeepSeek API)
  → deduplicate_relations.py → 1,176 条去重关系
  → build_graph.py → graph.json (1,068 节点, 1,091 边)
  → visualize/index.html → D3.js 可视化
```

## 核心数据

| 指标 | 数值 |
|------|------|
| 源 PDF 卷数 | 7 |
| 文章总数 | 421 |
| 时间跨度 | 1919-1985 |
| 去重人物 | 577 |
| 去重地点 | 323 |
| 去重关系 | 1,176 |
| 图谱节点 | 1,068 |
| 图谱边 | 1,091 |
| 社群数 | 479 (Louvain) |

## Top 10 (按关联度)

| 排名 | 人物 | 关联数 |
|------|------|--------|
| 1 | 毛泽东 | 173 |
| 2 | 蒋介石 | 105 |
| 3 | 中国共产党 | 39 |
| 4 | 周恩来 | 32 |
| 5 | 孙中山 | 28 |
| 6 | 斯大林 | 28 |
| 7 | 延安 | 26 |
| 8 | 列宁 | 23 |
| 9 | 希特勒 | 22 |
| 10 | 马克思 | 21 |

## 项目结构

```
260407mao/
├── .projectmemory/     # AI 助手交接文档（详细架构、数据清单、设计决策）
├── docs/               # 技术文档 & schema 定义
├── scripts/            # Python 管线脚本 (16 个)
├── tasks/              # 任务跟踪
├── visualize/          # D3.js 可视化 (index.html)
└── data/
    ├── clean/          # 清洗后 Markdown (7 卷)
    ├── metadata/       # QA 报告 + review 记录
    └── index/
        ├── articles/   # 文章切分 JSONL
        ├── entities/   # 人物 + 地点实体
        ├── relations/  # 关系 JSONL
        ├── archives/   # 908 个实体档案
        └── graph/      # D3.js 图谱 JSON
```

## 环境要求

```bash
pip install networkx python-louvain requests
```

实体/关系抽取需要 DeepSeek API key:
```bash
export DEEPSEEK_API_KEY=your-key-here
```

## 技术栈

- **语言**: Python 3
- **PDF 处理**: markitdown
- **LLM**: DeepSeek API (实体/关系抽取)
- **图谱**: NetworkX + python-louvain
- **可视化**: D3.js v7, 力导向图
- **数据格式**: JSONL, JSON, Markdown

## AI 助手须知

如果你是 AI 编程助手 (Claude Code, Cursor, Copilot 等)，请先看 `.projectmemory/` 文件夹:
- `overview.md` - 项目全貌
- `current-status.md` - 当前进度和待做事项
- `architecture.md` - 脚本依赖关系和数据结构
- `visualization.md` - 前端设计思路
- `known-issues.md` - 已知 bug
- `decisions.md` - 为什么这么设计

## License

本项目仅用于学习和研究目的。《毛泽东选集》原文版权归原出版方所有。
