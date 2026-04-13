# 转换工作流

## 总原则

- `pdf -> marker`
- `非 pdf -> markitdown`
- 当前 Phase 1 先围绕单一总集 PDF 跑通“按卷拆分 -> 卷级转换 -> 清洗 -> QA -> 人工复核记录”
- `marker` 仍是默认主路线，`markitdown` 是当前可用回退路径

## Phase 1 范围

当前只做五件事：

1. 书籍 PDF 入库
2. 总集按卷拆分
3. 卷级 PDF 转 Markdown
4. 清洗与质检
5. 人工复核记录

暂不进入 LLM 抽取、知识图谱、网站产品化。

## 当前样本

源文件：
- `data/raw/books/毛泽东选集(毛选1-7原版五卷+静火+赤旗+草堂) (毛泽东) (z-library.sk, 1lib.sk, z-lib.sk).pdf`

当前已确认：
- 第 1 卷边界：PDF 内部页码 `17–207`
- 卷 ID：`mao-volume-01`

## Phase 1 实际流程

### 1. 确认卷边界
- 优先用目录、书签、页内标题做半自动定位
- 最终边界由人工确认
- 将结果写入 `data/metadata/volume_manifest.json`

### 2. 拆分卷 PDF
运行：
```bash
python scripts/split_volumes.py
```

输出：
- `data/raw/books/volumes/mao-volume-01.pdf`

### 3. 转换卷 Markdown
默认建议：
```bash
python scripts/convert_volume.py mao-volume-01 --engine marker
```

当前可用回退：
```bash
python scripts/convert_volume.py mao-volume-01 --engine markitdown
```

输出：
- `data/markdown/marker/mao-volume-01.md` 或
- `data/markdown/markitdown/mao-volume-01.md`
- 对应日志写入 `data/staging/logs/`

### 4. 清洗 Markdown
运行：
```bash
python scripts/clean_markdown.py mao-volume-01
```

当前规则：
- 删除仅含数字的页码行
- 压缩连续 3 个及以上空行为 2 个空行
- 去掉行尾多余空格
- 保留标题、列表、引用、脚注原始结构

输出：
- `data/clean/volumes/mao-volume-01.cleaned.md`

备注：
- 原始 Markdown 若不是 UTF-8，清洗脚本会按 `utf-8 -> utf-8-sig -> gbk -> cp936` 顺序回退读取

### 5. 生成 QA 报告
运行：
```bash
python scripts/qa_volume.py mao-volume-01
```

输出：
- `data/metadata/qa/mao-volume-01.qa.json`

当前 QA 报告包含：
- 行数
- 标题数
- 空行数
- 纯数字行数
- 人工复核清单

### 6. sample 人工复核记录
运行前先初始化：
```bash
python scripts/init_review_manifest.py
```

复核入口：
- `data/metadata/review/review_manifest.json`
- `data/metadata/review/review_issues.jsonl`
- `docs/manual-review-workflow.md`

当前要求：
- 每卷在人工复核开始前，先把 `review_status` 设为 `in_progress`
- 发现问题后，向 `review_issues.jsonl` 追加一条记录
- 本轮复核完成后，更新 `issues_count`、`last_reviewed_at`，并将状态改为 `reviewed`

### 7. full review 阶段（已完成）
在 sample review 收口后，已按卷推进 full review 并完成 01–07 全部卷册。

执行约定：
- full review 复用 `review_manifest.json` 与 `review_issues.jsonl`
- `review_scope` 改为 `full` 表示进入整卷复核轮次
- full review 按卷记录，不细分章节或页段
- full review 的目标是确认该卷 `cleaned markdown` 是否足够稳定，可进入后续结构化抽取准备

当前状态：
- 01–07 全部卷册已完成 full review
- 所有卷册在 `review_manifest.json` 中标记为 `reviewed` / `full`
- 首轮 sample 与 full review 发现的问题已通过 TDD 修复并重跑全部卷册
- Phase 1 Markdown 基础产物已达到稳定状态，可进入 Phase 2

## Phase 2 结构化抽取工作流

Phase 2 目标：使用 LLM 对 cleaned markdown 进行结构化知识抽取，识别实体、关系，构建知识档案。

### Stage 1: Schema 设计与文档化（进行中）

**输入**：
- Phase 1 产出的 cleaned markdown（`data/clean/volumes/*.cleaned.md`）
- 项目需求文档（`docs/product-roadmap.md`、`docs/data-spec.md`）

**输出**：
- 实体 schema 文档（`docs/schema-entity.md`）
- 关系 schema 文档（`docs/schema-relation.md`）
- 档案 schema 文档（`docs/schema-archive.md`）
- 文章切分规则文档（`docs/article-segmentation.md`）
- LLM prompt 模板文档（`docs/extraction-prompts.md`）

**关键决策**：
- 抽取粒度：按文章粒度
- 输出格式：JSONL（实体、关系）+ JSON（档案）
- LLM 方案：DeepSeek API
- 实体类型：7 种（人物、事件、组织、地点、著作、概念、时间表达）

### Stage 2: 文章切分实现

**脚本**：`scripts/segment_articles.py`

**功能**：
- 读取 cleaned markdown
- 识别文章标题、日期、正文、注释边界
- 输出 JSONL 格式的文章列表

**运行**：
```bash
# 处理单卷
python scripts/segment_articles.py mao-volume-01

# 处理全部卷册
python scripts/segment_articles.py --all
```

**输出**：
- `data/index/articles/mao-volume-01.articles.jsonl`
- `data/index/articles/mao-volume-02.articles.jsonl`
- ...

### Stage 3: 实体抽取实现

**脚本**：`scripts/extract_entities.py`

**功能**：
- 读取文章 JSONL
- 调用 DeepSeek API 进行实体抽取
- 输出实体 JSONL

**运行**：
```bash
# 抽取单篇文章
python scripts/extract_entities.py --article mao-volume-01-article-001

# 抽取单卷所有文章
python scripts/extract_entities.py --volume mao-volume-01

# 抽取全部卷册
python scripts/extract_entities.py --all
```

**输出**：
- `data/index/entities/persons.jsonl`
- `data/index/entities/events.jsonl`
- `data/index/entities/organizations.jsonl`
- `data/index/entities/places.jsonl`
- `data/index/entities/works.jsonl`
- `data/index/entities/concepts.jsonl`
- `data/index/entities/time_expressions.jsonl`

### Stage 4: 关系抽取

**脚本**：`scripts/extract_relations.py`

**功能**：
- 基于已抽取的实体进行关系抽取
- 输出关系 JSONL

**输出**：
- `data/index/relations/relations.jsonl`

### Stage 5: 档案生成

**脚本**：`scripts/generate_archives.py`

**功能**：
- 聚合实体和关系
- 生成档案 JSON 文件

**输出**：
- `data/index/archives/person_archives/{entity_id}.json`
- `data/index/archives/event_archives/{entity_id}.json`
- `data/index/archives/organization_archives/{entity_id}.json`
- `data/index/archives/place_archives/{entity_id}.json`
- `data/index/archives/work_archives/{entity_id}.json`

当前 MVP 已完成：

1. 处理单一总集 PDF
2. 拆出 01–07 主线卷册
3. 跑通每卷完整闭环（拆分 -> 转换 -> 清洗 -> QA -> 人工复核）
4. 验证脚本、命名、清洗、QA 都可复用
5. 完成 sample review 与 full review 收口
6. Phase 1 Markdown 基础产物已稳定，可进入 Phase 2 结构化抽取准备

## 当前已知情况与策略

- `marker` 在当前环境曾因远端模型下载/网络问题失败
- 这不改变 `marker` 的主路线定位
- 当前执行策略：先用 `markitdown` 跑通闭环，已成功完成 01–07 全部卷册
- 清洗和 QA 只是基础质控，仍需人工检查正文完整性、段落连贯性、页码回溯、OCR 错字、脚注/表格异常
- Phase 1 已完成：01–07 全部卷册已完成 sample review 与 full review 收口
- Phase 1 Markdown 基础产物已稳定，下一步进入 Phase 2 结构化抽取准备
