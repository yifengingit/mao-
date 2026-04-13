# 人工复核工作流

## 目标

在卷级 `cleaned markdown + qa json` 已产出的基础上，为人工复核建立统一入口，确保每卷的复核状态、问题记录和后续修复动作都可追踪。

## 复核输入

每卷复核至少同时查看：

- `data/clean/volumes/<volume_id>.cleaned.md`
- `data/metadata/qa/<volume_id>.qa.json`
- `docs/qa-checklist.md`

## 复核输出

人工复核阶段新增两类产物：

- `data/metadata/review/review_manifest.json`
  - 记录每卷当前复核状态
- `data/metadata/review/review_issues.jsonl`
  - 逐条记录发现的问题

## 复核状态

`review_manifest.json` 中每卷使用以下状态：

- `pending`：尚未开始
- `in_progress`：正在复核
- `reviewed`：本轮复核已完成

复核范围使用：

- `sample`：抽样复核
- `full`：全量复核

## sample 与 full 的区别

### sample review

用于快速发现明显问题模式，确认该卷是否存在需要回修清洗规则或人工整理的共性问题。

特点：
- 允许只检查代表性片段
- 重点看开头结构、正文连贯性、注释区、OCR 明显错误
- 适合作为卷级闭环跑通后的第一轮筛查

### full review

用于按整卷完成通读/通检，确认该卷是否可以作为后续结构化抽取准备输入。

特点：
- 要求整卷检查完成后才能标记 `reviewed`
- 当前先按“卷”记录，不细分到章节、页段或进度百分比
- 发现问题仍复用既有 issue log 结构，不另起一套系统

## 问题严重度

问题统一分三级：

- `blocker`：严重影响后续抽取或内容可信度，需优先处理
- `major`：明显影响阅读、理解或局部抽取质量，建议尽快处理
- `minor`：不影响主流程，可延后处理

## 问题类型

优先复用当前项目已有质检语义：

- `ocr_bad`
- `layout_bad`
- `table_bad`
- `footnote_bad`
- `metadata_missing`
- `needs_manual_review`

如确有必要再补更细类型，但不要先过度设计。

## 单卷复核最小流程

1. 打开该卷 `cleaned.md`
2. 对照 `qa.json` 和 `docs/qa-checklist.md` 抽样或全量检查
3. 在 `review_manifest.json` 把该卷状态改为 `in_progress`
4. 发现问题时，向 `review_issues.jsonl` 追加一条 JSON 记录
5. 完成当前轮复核后：
   - 更新 `issues_count`
   - 更新 `last_reviewed_at`
   - 将状态改为 `reviewed`

## sample review 完成定义

满足以下条件即可：

- 已明确本轮复核范围为 `sample`
- 已检查对应卷的代表性片段
- 已记录发现的问题，或明确本轮未发现问题
- 已更新 `review_manifest.json` 中该卷状态

## full review 完成定义

满足以下条件即可：

- 已明确本轮复核范围为 `full`
- 已完成整卷检查
- 已记录发现的问题，或明确本轮未发现新增问题
- 已在 `notes` 中写明本轮 full review 结论
- 已更新 `review_manifest.json` 中该卷状态

## review manifest 使用约定

当前 full review 不新增字段，继续使用现有结构：

- `review_status = pending / in_progress / reviewed`
- `review_scope = sample / full`
- `issues_count` 记录当前仍未收口的问题数
- `last_reviewed_at` 记录最近一次复核日期
- `notes` 记录本轮结论

建议 full review 备注写法：
- 已完成 full review；未见新增阻断问题。
- 已完成 full review；存在若干 minor OCR 问题，暂不阻塞后续抽取准备。

## 问题记录建议字段

`review_issues.jsonl` 每条记录建议包含：

- `issue_id`
- `volume_id`
- `source_path`
- `line_start`
- `line_end`
- `severity`
- `issue_type`
- `summary`
- `detail`
- `suggested_action`
- `status`

其中：

- `suggested_action` 建议使用：`fix_cleaning_rule` / `manual_edit` / `defer`
- `status` 建议使用：`open` / `resolved` / `wont_fix`

## full review 中的问题记录约定

- full review 发现的问题，仍写入同一个 `review_issues.jsonl`
- 不新增 `sample_issue` / `full_issue` 之类字段
- 如需保留来源语境，可在 `detail` 或对应卷 `notes` 中写明“full review 发现”

## 当前建议节奏

1. 先完成 01–07 的 sample review 收口
2. 再补 full review 模板，明确按卷记录约定
3. 选定 1 卷作为 full review 模板卷试跑
4. 模板稳定后，再决定是否逐卷推进 full review
5. full review 稳定后，才进入结构化抽取准备
