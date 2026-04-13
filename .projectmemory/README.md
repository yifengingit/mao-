# .projectmemory - AI 助手交接文档

这个文件夹是给下一个 AI 编程助手（Claude Code、Cursor、Copilot 等）看的。
打开任意一个文件就能快速了解项目全貌。

## 文件索引

| 文件 | 内容 | 什么时候看 |
|------|------|-----------|
| [overview.md](overview.md) | 项目一句话介绍 + 架构总览 + 数据流 | **第一个看这个** |
| [current-status.md](current-status.md) | 已完成/进行中/待做的事 | 接手时先看 |
| [architecture.md](architecture.md) | 数据管线、脚本依赖关系、文件结构 | 改代码前看 |
| [data-inventory.md](data-inventory.md) | 每个数据文件是什么、多大、怎么来的 | 调数据时查 |
| [visualization.md](visualization.md) | 前端可视化的设计思路和当前状态 | 改前端前看 |
| [known-issues.md](known-issues.md) | 已知 bug、技术债、API 问题 | debug 时查 |
| [decisions.md](decisions.md) | 为什么这么设计（关键决策记录） | 想改架构前看 |

## 快速上手

```bash
# 1. 看可视化（最直观）
cd 260407mao
python -m http.server 8766
# 浏览器打开 http://localhost:8766/visualize/index.html

# 2. 看数据
cat data/index/graph/graph.json | python -m json.tool | head -50

# 3. 重新构建图谱（如果改了数据）
python scripts/build_graph.py
python scripts/build_article_excerpts.py
```
