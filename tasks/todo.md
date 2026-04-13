# TODO

## Phase 0 - Scaffold
- [x] 创建基础目录结构
- [x] 写入 README
- [x] 写入数据规范文档
- [x] 写入转换工作流文档
- [x] 写入质检清单
- [x] 写入产品路线图
- [x] 初始化任务文件

## Phase 1 - Volume 01 Closed Loop
- [x] 确认总集 PDF 的第 1 卷边界（17–207）
- [x] 写入 `data/metadata/volume_manifest.json`
- [x] 拆出第 1 卷 PDF
- [x] 验证第 1 卷可回溯到原总 PDF 页码
- [x] 支持卷级转换脚本 `scripts/convert_volume.py`
- [x] 用 `markitdown` 跑通 `mao-volume-01` 原始 Markdown
- [x] 建立清洗规则 `docs/cleaning-rules.md`
- [x] 产出 `data/clean/volumes/mao-volume-01.cleaned.md`
- [x] 生成 `data/metadata/qa/mao-volume-01.qa.json`
- [x] 同步 README / conversion workflow / todo 文档

## Phase 1 - Next
- [x] 人工抽查 `mao-volume-01.cleaned.md` 正文质量
- [x] 用最小 TDD 修复正文硬换行、伪段落断裂、日期/小节标题误合并回归
- [x] 决定 Phase 1 主线继续以 `markitdown + clean_markdown.py` 为基线，`marker` 降级为非阻塞验证项
- [x] 补第 2 卷边界并扩展 manifest，产出 `mao-volume-02` 的 PDF / raw markdown / cleaned markdown / QA
- [x] 确认第 3–7 卷主线边界并扩展 manifest（第 6/7 卷按静火版纳入，1808 起赤旗版单列到后续材料阶段）
- [x] 将相同流程复制到后续卷册

## Phase 1.5 - Manual Review Layer
- [x] 新增人工复核工作流文档 `docs/manual-review-workflow.md`
- [x] 初始化 `data/metadata/review/review_manifest.json`
- [x] 建立问题记录入口 `data/metadata/review/review_issues.jsonl`
- [x] 同步 README / conversion workflow / todo 文档
- [x] 启动第 1 批人工复核（先从 `mao-volume-01` 开始）

## Phase 1.6 - Full Review Template
- [x] 明确 full review 先按卷记录，不细分章节或页段
- [x] 更新 `docs/manual-review-workflow.md`，区分 sample / full
- [x] 同步 README / `docs/conversion-workflow.md` 中的 full review 阶段说明
- [x] 选定 `mao-volume-02` 作为 full review 模板卷（先不必立刻执行全量复核）
- [x] 执行 `mao-volume-02` full review，发现并修复 `review-issue-0003` 短断裂问题
- [x] 重跑 01–07 全部卷册 cleaned markdown，确保新规则无回归
- [x] 逐卷推进 full review（03–07），确认无新增 major 问题
- [x] 更新 `review_manifest.json`，01–07 全部标记为 `reviewed` / `full`

## Phase 2 - 结构化抽取

### Phase 2.1 - Stage 1: Schema 设计与文档化
- [x] 创建实体 schema 文档（`docs/schema-entity.md`）
- [x] 创建关系 schema 文档（`docs/schema-relation.md`）
- [x] 创建档案 schema 文档（`docs/schema-archive.md`）
- [x] 创建文章切分规则文档（`docs/article-segmentation.md`）
- [x] 创建 LLM prompt 模板文档（`docs/extraction-prompts.md`，使用 DeepSeek API）
- [x] 更新 `docs/data-spec.md`，补充 Phase 2 目录结构
- [x] 更新 `README.md`，补充 Phase 2 当前状态
- [x] 更新 `docs/conversion-workflow.md`，增加 Phase 2 工作流说明
- [x] 更新 `docs/product-roadmap.md`，更新 Phase 2 进度
- [x] 更新 `tasks/todo.md`，新增 Phase 2 任务清单

### Phase 2.2 - Stage 2: 文章切分实现
- [x] 实现文章切分脚本（`scripts/segment_articles.py`）
- [x] 对 volume-01 进行切分测试
- [x] 人工抽查切分结果，验证边界识别准确率
- [x] 批量处理全部 7 卷，输出到 `data/index/articles/`
- [x] 生成文章切分统计报告

### Phase 2.3 - Stage 3: 实体抽取实现（人物）
- [x] 实现实体抽取脚本（`scripts/extract_entities.py`）
- [x] 配置 DeepSeek API 调用
- [x] 选择 volume-01 进行测试，优化 prompt 排除神话人物
- [x] 实现超时重试机制和内容长度优化
- [x] 批量抽取全部 7 卷，输出到 `data/index/entities/persons.jsonl`
- [x] 生成完整抽取报告（`extraction-final-report.md`）

### Phase 2.4 - 实体质量提升与扩展
- [x] 人物实体去重与合并（同一人物在不同文章中的出现）
  - 去重前：1,746 条 -> 去重后：577 条
  - 去重率：67.0%
  - 数据完整性验证通过（mentions 总数保持 3,044）
- [ ] 处理剩余 110 篇失败文章（API 错误或空内容）
- [ ] 人工抽查验证人物抽取质量（随机抽取 20 篇）
- [ ] 扩展到其他实体类型（暂缓，优先完成人物实体全流程）：
  - [ ] 地点实体抽取（已实现脚本，但 API 失败率 60%，需优化）
  - [ ] 组织实体抽取（已实现脚本，未测试）
  - [ ] 事件实体抽取
  - [ ] 著作实体抽取
  - [ ] 概念实体抽取
  - [ ] 时间表达抽取

### Phase 2.5 - 关系与档案
- [x] 实现关系抽取脚本（`scripts/extract_relations.py`）
  - [x] 设计关系抽取 prompt
  - [x] 实现人物-人物关系抽取
  - [x] 实现人物-组织关系抽取（基于文本推断）
- [x] 批量抽取人物间关系（1,451 个原始关系）
- [x] 关系去重与合并（1,176 个唯一关系，去重率 19%）
- [x] 实现档案生成脚本（`scripts/generate_archives.py`）
- [x] 生成人物档案与地点档案（聚合实体、关系、文献来源）
  - 人物档案：585 个，含关联人物/组织/来源文献
  - 地点档案：323 个，含地点类型/现代名称/来源文献
  - 全局索引：`data/index/archives/index.json`（908 条）
  - 已知问题：部分实体的 merged_articles 未完整追踪（上游抽取历史问题），references 章节仅作参考

## Deferred After Phase 1
- [ ] 设计结构化抽取字段
- [ ] 设计切片与索引格式
- [ ] 设计人物/事件/组织/地点/著作档案 schema
- [ ] 设计概念卡片 schema
- [ ] 设计内部交叉链接规则
- [ ] 评估 graphify 等可复用图谱项目

## Review
- Phase 1 已完成：01–07 全部卷册已跑通完整闭环（拆分 -> 转换 -> 清洗 -> QA -> sample review -> full review）
- Phase 1 主线采用 `markitdown + clean_markdown.py` 基线；`marker` 因远端模型下载问题暂未使用
- 清洗规则已完成四轮 TDD 回归修复：
  - 正文硬换行合并
  - 伪段落错误空行处理
  - 日期/小节标题误合并修复
  - 短断裂跨空行合并（review-issue-0003）
- 所有修复均已补充单元测试，当前测试套件 15/15 通过
- 01–07 全部卷册已重跑 cleaned markdown，确保新规则无回归
- 首轮 sample review 与 full review 发现的问题（review-issue-0001/0002/0003）已全部修复并标记为 `resolved`
- `review_manifest.json` 中 01–07 全部标记为 `reviewed` / `full`，`issues_count` 均为 0
- Phase 1 Markdown 基础产物已达到稳定状态，可进入 Phase 2 结构化抽取准备
- Phase 2 Stage 1-3 已完成：
  - Schema 设计：完成 5 个 schema 文档、1 个 prompt 模板文档、更新 4 个项目文档
  - 文章切分：421 篇文章，7 卷全覆盖，输出到 `data/index/articles/`
  - 人物实体抽取：1,746 条原始记录，311/421 篇文章（73.9%）
  - 人物实体去重：1,746 -> 577 条（去重率 67.0%），数据完整性验证通过
- Phase 2 架构决策：按文章粒度抽取、使用 DeepSeek API、JSONL 格式存储实体和关系、JSON 格式存储档案
- Phase 2 技术优化：实现超时重试机制（3次重试，指数退避）、内容长度限制（5000字）、null 内容检查
- Phase 2 去重策略：精确名称匹配、别名聚合、属性合并、mentions 完整保留
- Phase 2.4/2.5 已完成（2026-04-13）：
  - 补跑 110 篇失败文章（人物抽取），成功率 100%，耗时约 58 分钟
  - 人物实体去重更新：662 -> 585 条（去重率 11.6%）
  - 地点实体去重：777 -> 323 条（去重率 58.4%）
  - 档案生成完毕：585 人物档案 + 323 地点档案 + 全局索引
