# 已知问题

## 数据层

### 110 篇文章抽取失败
- **严重性**: 中等 (26% 文章缺失实体数据)
- **原因**: DeepSeek API 超时、JSON 格式不一致、大文章 token 超限
- **主要集中**: volume-06
- **修复方案**: `python scripts/retry_failed_articles.py` (已就绪，未运行)
- **影响**: 这些文章的实体和关系不在 graph.json 中

### 组织实体不完整
- **现状**: 没有专门的组织实体抽取步骤。当前 156 个组织节点是从关系的 from/to entity 中间接提取的。
- **结果**: 组织节点没有 aliases、mention_count 等详细属性，只有 node_type="organization"

### 地点实体的 modern_name 字段
- 地点实体有 `attributes.modern_name` 字段 (如 "延安" -> 现代地名)
- 但只有部分地点填写了这个字段

## 可视化层

### zoom-to-fit 定位偏移
- **现象**: 图谱在画布上偏下方，上部留有大片空白
- **可能原因**:
  1. `zoomToFit()` 计算 `H` 时包含了 timeline 区域 (~90px)
  2. forceCenter 强度太弱 (0.08)，节点没有完全居中
- **修复建议**: 在 `zoomToFit` 中减去 timeline 高度，或增加 forceCenter 强度到 0.15

### 密度切换性能
- 每次切换密度 (精要/扩展/全量) 会完全销毁 D3 simulation 并重建
- 全量模式 (1068 节点) 重建需要几秒
- 有 loading overlay 但体验不够流畅
- **优化方向**: 改为 toggle display:none 而不是重建 simulation

### evidence_items context 截断
- 关系的 evidence_items[].context 字段有的很短 (几个字)，有的很长
- 右面板显示时没有做 truncation，可能溢出
- 节点的来源段落只取了前 5 条，排序按 first_date

### 标签重叠
- 精要模式 (99 节点) 时所有标签都显示
- 某些密集区域标签会重叠
- 可考虑: collision detection for labels, 或只显示 top-N 标签

## API / 环境

### DeepSeek API key
- 原来硬编码在 `extract_entities.py` 和 `extract_relations.py` 中
- **已修复**: 改为 `os.environ.get("DEEPSEEK_API_KEY", "")`
- 使用时需要: `export DEEPSEEK_API_KEY=your-key-here`

### marker PDF 解析器
- `marker` 是首选 PDF 解析器，但在当前 Windows 环境下因远端模型下载问题受阻
- 实际使用的是 `markitdown` 作为回退
- markitdown 输出可能不是 UTF-8 (gbk/cp936)，clean_markdown.py 已处理

### Python 环境
- Python 3.13 on Windows 11
- 没有 requirements.txt 或 pyproject.toml
- 需要手动安装: `pip install networkx python-louvain requests`

## 代码质量

### load_jsonl 重复
- 几乎每个脚本都有自己的 `load_jsonl()` 函数副本
- 没有公共 utils 模块
- 不影响功能，但代码重复

### 没有测试
- `tests/` 目录存在但为空
- 所有验证都是通过运行脚本 + 人工检查
- `validate_deduplication.py` 算是唯一的自动化验证

### 没有 requirements.txt
- 依赖关系没有锁定
- 需要创建: `pip freeze > requirements.txt` 或写一个 pyproject.toml
