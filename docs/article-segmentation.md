# 文章切分规则

## 概述

本文档定义如何从 cleaned markdown 文件中识别文章边界，将整卷文本切分为独立的文章单元。文章是 Phase 2 实体抽取的基本单位。

## 文章结构

每篇文章通常包含以下部分：

1. **文章标题**：纯文本行，可能带 `*` 后缀（表示有题注）
2. **日期行**：紧跟标题行，格式为 `（一九XX年XX月XX日）`
3. **正文内容**：文章主体部分
4. **注释区域**（可选）：以 `　注　　释` 开始，包含题注和脚注

## 识别规则

### 1. 文章标题识别

**规则**：
- 非空行
- 不以数字开头（排除页码行）
- 不是注释标记行（`　注　　释`）
- 不是脚注行（不以 `〔数字〕` 开头）
- 后续行是日期行或空行

**标题变体**：
- 带题注标记：`中国社会各阶级的分析*`
- 不带标记：`湖南农民运动考察报告`

**示例**：
```
中国社会各阶级的分析*

（一九二五年十二月一日）
```

### 2. 日期行识别

**规则**：
- 格式：`（一九XX年XX月XX日）` 或 `（一九XX年XX月）` 或 `（一九XX年）`
- 使用全角括号 `（）`
- 使用中文数字：`一二三四五六七八九○`
- 紧跟标题行之后（中间可能有空行）

**日期格式变体**：
- 完整日期：`（一九二五年十二月一日）`
- 年月：`（一九二七年三月）`
- 仅年份：`（一九三五年）`
- 日期范围：`（一九二六年十二月至一九二七年二月）`
- 不确定日期：`（一九二七年春）`

**正则表达式**：
```python
import re

DATE_PATTERN = re.compile(
    r'[（(]'  # 左括号（全角或半角）
    r'一九[○〇零一二三四五六七八九]{2}年'  # 年份
    r'(?:'  # 可选的月日部分
        r'(?:[一二三四五六七八九十]+月)?'  # 月份
        r'(?:[一二三四五六七八九十]+日)?'  # 日期
        r'|春|夏|秋|冬'  # 或季节
    r')?'
    r'[）)]'  # 右括号
)
```

### 3. 注释区域识别

**规则**：
- 以 `　注　　释` 开始（注意空格为全角空格）
- 包含题注（带 `*` 标记）和脚注（带 `〔数字〕` 标记）
- 注释区域延续到下一篇文章标题或文件结束

**注释类型**：

1. **题注**：
   - 格式：`　*　毛泽东此文是为...`
   - 解释文章背景、写作目的等

2. **脚注**：
   - 格式：`〔1〕国家主义派指...`
   - 解释正文中的术语、人名、事件等

**示例**：
```
　注　　释
　*　毛泽东此文是为反对当时党内存在着的两种倾向而写的。当时党内的第一种倾向，以陈独秀为代表...

〔1〕国家主义派指中国青年党，当时以其外围组织"中国国家主义青年团"的名义公开进行活动...

〔2〕戴季陶（一八九一——一九四九），又名传贤，原籍浙江湖州，生于四川广汉...
```

### 4. 正文内容识别

**规则**：
- 从日期行之后开始
- 到注释区域开始或下一篇文章标题为止
- 包含所有段落、空行

## 切分算法

### 伪代码

```python
def segment_articles(cleaned_markdown_lines):
    articles = []
    current_article = None
    in_notes = False
    
    for i, line in enumerate(lines):
        # 检查是否是注释区域开始
        if line.strip() == '注　　释':
            in_notes = True
            if current_article:
                current_article['content_end'] = i - 1
                current_article['notes_start'] = i
            continue
        
        # 检查是否是文章标题
        if is_title_line(line, lines[i+1:i+3]):
            # 保存上一篇文章
            if current_article:
                if in_notes:
                    current_article['notes_end'] = i - 1
                else:
                    current_article['content_end'] = i - 1
                articles.append(current_article)
            
            # 开始新文章
            current_article = {
                'title': line.strip().rstrip('*'),
                'has_title_note': line.strip().endswith('*'),
                'title_line': i,
                'date': None,
                'date_line': None,
                'content_start': None,
                'content_end': None,
                'notes_start': None,
                'notes_end': None
            }
            in_notes = False
            continue
        
        # 检查是否是日期行
        if current_article and not current_article['date']:
            date_match = DATE_PATTERN.search(line)
            if date_match:
                current_article['date'] = date_match.group(0)
                current_article['date_line'] = i
                current_article['content_start'] = i + 1
                continue
    
    # 保存最后一篇文章
    if current_article:
        if in_notes:
            current_article['notes_end'] = len(lines) - 1
        else:
            current_article['content_end'] = len(lines) - 1
        articles.append(current_article)
    
    return articles
```

### 辅助函数

```python
def is_title_line(line, next_lines):
    """判断是否是文章标题行"""
    if not line.strip():
        return False
    
    # 排除页码行
    if line.strip().isdigit():
        return False
    
    # 排除注释标记
    if '注　　释' in line:
        return False
    
    # 排除脚注
    if re.match(r'^〔\d+〕', line.strip()):
        return False
    
    # 检查后续行是否是日期行
    for next_line in next_lines[:3]:
        if not next_line.strip():
            continue
        if DATE_PATTERN.search(next_line):
            return True
        break
    
    return False

def parse_date(date_str):
    """将中文日期转换为 ISO 格式"""
    # 示例实现
    year_match = re.search(r'一九([○〇零一二三四五六七八九]{2})年', date_str)
    if not year_match:
        return None
    
    year_cn = year_match.group(1)
    year = 1900 + chinese_to_arabic(year_cn)
    
    month_match = re.search(r'([一二三四五六七八九十]+)月', date_str)
    month = chinese_to_arabic(month_match.group(1)) if month_match else 1
    
    day_match = re.search(r'([一二三四五六七八九十]+)日', date_str)
    day = chinese_to_arabic(day_match.group(1)) if day_match else 1
    
    return f"{year:04d}-{month:02d}-{day:02d}"

def chinese_to_arabic(cn_num):
    """中文数字转阿拉伯数字"""
    mapping = {
        '○': 0, '〇': 0, '零': 0,
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    }
    # 简化实现，实际需要处理十位、个位组合
    result = 0
    for char in cn_num:
        result = result * 10 + mapping.get(char, 0)
    return result
```

## 输出格式

### JSONL 格式

每篇文章输出为一行 JSON：

```json
{
  "article_id": "mao-volume-01-article-001",
  "volume_id": "mao-volume-01",
  "title": "中国社会各阶级的分析",
  "has_title_note": true,
  "date_original": "（一九二五年十二月一日）",
  "date_iso": "1925-12-01",
  "title_line": 32,
  "date_line": 34,
  "content_lines": {
    "start": 36,
    "end": 50
  },
  "notes_lines": {
    "start": 52,
    "end": 99
  },
  "word_count": 3542,
  "paragraph_count": 15
}
```

### 字段说明

- **article_id**: 文章唯一标识符
  - 格式：`{volume_id}-article-{seq:03d}`
  - 示例：`mao-volume-01-article-001`

- **volume_id**: 所属卷册 ID

- **title**: 文章标题（去除 `*` 标记）

- **has_title_note**: 是否有题注

- **date_original**: 原始日期字符串

- **date_iso**: ISO 8601 格式日期

- **title_line**: 标题所在行号

- **date_line**: 日期所在行号

- **content_lines**: 正文行号范围
  - `start`: 起始行号
  - `end`: 结束行号

- **notes_lines**: 注释行号范围（可选）
  - `start`: 起始行号
  - `end`: 结束行号

- **word_count**: 字数统计（不含标点和空格）

- **paragraph_count**: 段落数量

## 边界情况处理

### 1. 缺少日期的文章

某些文章可能没有明确的日期行：
- 前言、说明、序言等
- 处理：`date_iso` 设为 `null`，`content_start` 从标题下一行开始

### 2. 连续的注释区域

某些卷册可能在文章之间有独立的注释区域：
- 处理：将其归入前一篇文章的注释部分

### 3. 特殊标题格式

某些标题可能跨多行或包含副标题：
- 处理：将连续的非空行合并为完整标题，直到遇到日期行

### 4. 文件开头的元数据

卷册开头可能有出版说明、目录等：
- 处理：作为独立文章处理，`article_id` 使用 `000` 序号

## 验证规则

切分结果需满足以下条件：

1. **完整性**：所有行都应归属于某篇文章
2. **无重叠**：文章之间的行号范围不应重叠
3. **有序性**：文章按行号顺序排列
4. **标题必需**：每篇文章必须有标题
5. **行号连续**：相邻文章的行号应基本连续（允许少量空行）

## 统计输出

切分完成后输出统计信息：

```json
{
  "volume_id": "mao-volume-01",
  "total_lines": 2995,
  "total_articles": 18,
  "articles_with_notes": 15,
  "articles_without_date": 2,
  "average_article_length": 166,
  "longest_article": {
    "article_id": "mao-volume-01-article-005",
    "title": "湖南农民运动考察报告",
    "line_count": 450
  },
  "shortest_article": {
    "article_id": "mao-volume-01-article-000",
    "title": "第一卷第二版出版说明",
    "line_count": 15
  }
}
```
