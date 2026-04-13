# 项目总览

## 一句话

把《毛泽东选集》7 卷 421 篇文章，从 PDF 变成知识图谱，最终做成可交互的 D3.js 可视化。

## 项目性质

- **类型**: Portfolio / showcase 项目
- **目标受众**: 历史学、中国研究方向的学术/研究人员
- **不是**: 商业产品、学术论文

## 管线总览

```
PDF (15MB, 7卷)
  ↓ split_volumes.py
7 个卷 PDF
  ↓ convert_volume.py (markitdown)
7 个原始 Markdown
  ↓ clean_markdown.py
7 个清洗后 Markdown (5.4MB)        ← data/clean/volumes/
  ↓ segment_articles.py
421 篇文章 JSONL                    ← data/index/articles/
  ↓ extract_entities.py (DeepSeek API)
1,746 条人物 + 地点实体
  ↓ deduplicate_entities.py
577 人物 + ~323 地点（去重后）       ← data/index/entities/
  ↓ extract_relations.py (DeepSeek API)
1,451 条关系
  ↓ deduplicate_relations.py
1,176 条关系（去重后）               ← data/index/relations/
  ↓ generate_archives.py
908 个实体档案 JSON                  ← data/index/archives/
  ↓ build_graph.py + analyze_graph.py
graph.json (D3.js 格式)             ← data/index/graph/
  ↓ build_article_excerpts.py
article_excerpts.json               ← data/index/graph/
  ↓
visualize/index.html                ← 最终可视化
```

## 核心数字

| 指标 | 数值 |
|------|------|
| 源 PDF 卷数 | 7 |
| 文章总数 | 421 |
| 时间跨度 | 1919-1985 |
| 去重后人物 | 577 |
| 去重后地点 | ~323 |
| 去重后关系 | 1,176 |
| 实体档案 | 908 |
| 图谱节点 | 1,068 |
| 图谱边 | 1,091 |
| 社群数（Louvain） | 479 |

## 技术栈

- **语言**: Python 3.13
- **PDF 处理**: markitdown (回退), marker (主选但环境问题未解决)
- **LLM**: DeepSeek API (deepseek-chat) 用于实体/关系抽取
- **图谱构建**: NetworkX + python-louvain (社群检测) + betweenness centrality
- **可视化**: D3.js v7, 力导向图, SVG
- **数据格式**: JSONL (行分隔 JSON), Markdown

## 文件结构

```
260407mao/
├── .gitignore
├── .projectmemory/     ← 你正在看的交接文档
├── README.md           ← GitHub 展示页
├── docs/               ← 技术文档 & schema 定义
├── scripts/            ← 全部 Python 脚本（管线的每一步）
├── tasks/              ← 任务跟踪 (todo.md, lessons.md)
├── tests/              ← 测试（目前为空）
├── visualize/          ← D3.js 可视化 (index.html)
└── data/
    ├── raw/            ← [gitignore] 原始 PDF
    ├── markdown/       ← [gitignore] 工具原始输出
    ├── staging/        ← [gitignore] 临时文件
    ├── clean/          ← 清洗后 Markdown（7卷）
    ├── metadata/       ← QA 报告 + review 记录
    └── index/          ← 结构化输出
        ├── articles/   ← 文章切分 JSONL
        ├── entities/   ← 实体 JSONL（去重后）
        ├── relations/  ← 关系 JSONL（去重后）
        ├── archives/   ← 实体档案 JSON
        └── graph/      ← D3.js 图谱 JSON
```
