# 卷级拆分规范

## 目标

将总集 PDF 拆分为可独立处理的卷级 PDF，作为 Phase 1 的正式输入单位。

## 源文件

- 原始文件目录：`data/raw/books/`
- 当前源文件：`毛泽东选集(毛选1-7原版五卷+静火+赤旗+草堂) (毛泽东) (z-library.sk, 1lib.sk, z-lib.sk).pdf`

## 命名规则

- 卷级 PDF：`mao-volume-01.pdf`、`mao-volume-02.pdf`
- marker 原始 markdown：`data/markdown/marker/mao-volume-01.md`
- markitdown 对照 markdown：`data/markdown/markitdown/mao-volume-01.md`
- 清洗后 markdown：`data/clean/volumes/mao-volume-01.cleaned.md`
- QA 报告：`data/metadata/qa/mao-volume-01.qa.json`

## 卷清单字段

每卷记录以下字段：
- `volume_id`
- `title`
- `source_pdf`
- `start_page`
- `end_page`
- `notes`

页码统一使用 pypdf 的 0-based 半开区间思维来实现，但在文档描述中额外写清楚原 PDF 人类阅读页码。

## 处理原则

- 原始总 PDF 不修改
- 所有卷级 PDF 从总 PDF 派生
- 每卷必须能回溯到总 PDF 页码范围
- Phase 1 先完整打通 `mao-volume-01`
