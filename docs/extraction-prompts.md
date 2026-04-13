# LLM 抽取 Prompt 模板

## 概述

本文档定义使用 DeepSeek API 进行实体抽取的 prompt 模板。每种实体类型使用独立的 prompt，确保抽取质量和一致性。

## API 配置

### DeepSeek API 信息

- **API Key**: `sk-c2713d1281f0406ca45bc523b0b4863a`
- **Base URL**: `https://api.deepseek.com/v1`
- **模型**: `deepseek-chat`
- **输出格式**: JSON

### 调用示例

```python
import requests

def call_deepseek_api(prompt, system_message):
    headers = {
        "Authorization": "Bearer sk-c2713d1281f0406ca45bc523b0b4863a",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()
```

## 通用 Prompt 结构

所有实体抽取 prompt 遵循以下结构：

1. **System Message**: 定义任务角色和输出要求
2. **任务说明**: 明确抽取目标
3. **实体定义**: 详细说明什么算该类型实体
4. **输出格式**: JSON schema 示例
5. **Few-shot 示例**: 2-3 个标注好的例子
6. **输入文本**: 待抽取的文章内容

## 1. 人物（Person）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取人物实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的人物，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有人物实体。

## 实体定义

人物实体包括：
- 历史人物：政治家、军事家、思想家、革命家等
- 作者和编者
- 文章中提到的具体个人
- 不包括：泛指的群体（如"工人"、"农民"）

## 输出格式

返回 JSON 对象，包含 persons 数组：

{
  "persons": [
    {
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {
        "birth_year": "出生年份（如有）",
        "roles": ["角色1", "角色2"],
        "affiliations": ["所属组织1"]
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
毛泽东此文是为反对当时党内存在着的两种倾向而写的。当时党内的第一种倾向，以陈独秀为代表，只注意同国民党合作，忘记了农民，这是右倾机会主义。第二种倾向，以张国焘为代表，只注意工人运动，同样忘记了农民，这是"左"倾机会主义。
```

输出：
```json
{
  "persons": [
    {
      "name": "毛泽东",
      "aliases": [],
      "attributes": {
        "roles": ["革命家", "政治家"],
        "affiliations": ["中国共产党"]
      },
      "mentions": [
        {
          "line_start": 53,
          "line_end": 53,
          "context": "...毛泽东此文是为反对当时党内存在着的两种倾向而写的..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "陈独秀",
      "aliases": [],
      "attributes": {
        "roles": ["政治家"],
        "affiliations": ["中国共产党"]
      },
      "mentions": [
        {
          "line_start": 53,
          "line_end": 54,
          "context": "...当时党内的第一种倾向，以陈独秀为代表，只注意同国民党合作..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "张国焘",
      "aliases": [],
      "attributes": {
        "roles": ["政治家"],
        "affiliations": ["中国共产党"]
      },
      "mentions": [
        {
          "line_start": 54,
          "line_end": 55,
          "context": "...第二种倾向，以张国焘为代表，只注意工人运动..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 2. 事件（Event）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取事件实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的历史事件，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有事件实体。

## 实体定义

事件实体包括：
- 历史运动：五卅运动、农民运动等
- 重要会议：党代会、政治会议等
- 军事行动：战役、罢工、起义等
- 重大事件：惨案、政变等
- 不包括：日常活动、泛指的行为

## 输出格式

返回 JSON 对象，包含 events 数组：

{
  "events": [
    {
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {
        "start_date": "开始日期（ISO格式，如有）",
        "end_date": "结束日期（可选）",
        "location": "发生地点",
        "event_type": "事件类型"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
我们从一九二五年的五卅运动和各地农民运动的经验看来，这个断定是不错的。
```

输出：
```json
{
  "events": [
    {
      "name": "五卅运动",
      "aliases": ["五卅惨案"],
      "attributes": {
        "start_date": "1925-05-30",
        "location": "上海",
        "event_type": "反帝爱国运动"
      },
      "mentions": [
        {
          "line_start": 40,
          "line_end": 40,
          "context": "...我们从一九二五年的五卅运动和各地农民运动的经验看来..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "农民运动",
      "aliases": [],
      "attributes": {
        "start_date": "1925",
        "event_type": "社会运动"
      },
      "mentions": [
        {
          "line_start": 40,
          "line_end": 40,
          "context": "...我们从一九二五年的五卅运动和各地农民运动的经验看来..."
        }
      ],
      "confidence": 0.9
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 3. 组织（Organization）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取组织实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的组织机构，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有组织实体。

## 实体定义

组织实体包括：
- 政党：中国共产党、国民党等
- 政府机构：国民政府、苏维埃政府等
- 军事组织：红军、国民革命军等
- 社会团体：工会、农会、秘密会社等
- 国际组织：共产国际、国际联盟等
- 不包括：泛指的群体（如"地主阶级"）

## 输出格式

返回 JSON 对象，包含 organizations 数组：

{
  "organizations": [
    {
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {
        "founded_date": "成立日期（如有）",
        "organization_type": "组织类型",
        "headquarters": "总部所在地"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
一九二二年中国共产党参加共产国际，成为它的一个支部。
```

输出：
```json
{
  "organizations": [
    {
      "name": "中国共产党",
      "aliases": ["中共", "共产党"],
      "attributes": {
        "founded_date": "1921-07-23",
        "organization_type": "政党"
      },
      "mentions": [
        {
          "line_start": 77,
          "line_end": 77,
          "context": "...一九二二年中国共产党参加共产国际，成为它的一个支部..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "共产国际",
      "aliases": ["第三国际"],
      "attributes": {
        "founded_date": "1919-03",
        "organization_type": "国际组织"
      },
      "mentions": [
        {
          "line_start": 77,
          "line_end": 78,
          "context": "...一九二二年中国共产党参加共产国际，成为它的一个支部..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 4. 地点（Place）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取地点实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的地理位置，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有地点实体。

## 实体定义

地点实体包括：
- 国家：中国、苏联、日本等
- 省份：湖南、湖北、江西等
- 城市：上海、北京、广州等
- 县市：湘潭、长沙、武汉等
- 村镇：韶山、井冈山等
- 地理区域：华北、江南等
- 不包括：方位词（如"东方"、"西方"）

## 输出格式

返回 JSON 对象，包含 places 数组：

{
  "places": [
    {
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {
        "place_type": "地点类型",
        "parent_place": "上级行政区划"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
一九二五年五月间，上海、青岛的日本纱厂先后发生工人罢工的斗争。
```

输出：
```json
{
  "places": [
    {
      "name": "上海",
      "aliases": [],
      "attributes": {
        "place_type": "城市",
        "parent_place": "中国"
      },
      "mentions": [
        {
          "line_start": 89,
          "line_end": 90,
          "context": "...一九二五年五月间，上海、青岛的日本纱厂先后发生工人罢工的斗争..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "青岛",
      "aliases": [],
      "attributes": {
        "place_type": "城市",
        "parent_place": "山东"
      },
      "mentions": [
        {
          "line_start": 89,
          "line_end": 90,
          "context": "...一九二五年五月间，上海、青岛的日本纱厂先后发生工人罢工的斗争..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 5. 著作（Work）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取著作实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的书籍、文章、报刊，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有著作实体。

## 实体定义

著作实体包括：
- 书籍：《资本论》、《毛泽东选集》等
- 文章：《矛盾论》、《实践论》等
- 报刊：《晨报》、《新青年》等
- 文献：宣言、决议、报告等
- 不包括：泛指的文体（如"文章"、"书籍"）

## 输出格式

返回 JSON 对象，包含 works 数组：

{
  "works": [
    {
      "name": "标准名称",
      "aliases": ["别名1"],
      "attributes": {
        "author": "作者（如有）",
        "work_type": "著作类型"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
有一个自称为戴季陶"真实信徒"的，在北京《晨报》上发表议论说："举起你的左手打倒帝国主义，举起你的右手打倒共产党。"
```

输出：
```json
{
  "works": [
    {
      "name": "晨报",
      "aliases": ["北京晨报"],
      "attributes": {
        "work_type": "报刊"
      },
      "mentions": [
        {
          "line_start": 38,
          "line_end": 38,
          "context": "...有一个自称为戴季陶"真实信徒"的，在北京《晨报》上发表议论说..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 6. 概念（Concept）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取概念实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确的理论概念和术语，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有概念实体。

## 实体定义

概念实体包括：
- 政治概念：阶级斗争、无产阶级专政、民主集中制等
- 经济概念：生产关系、剥削、资本主义等
- 哲学概念：辩证法、唯物主义、矛盾等
- 军事概念：游击战、持久战等
- 社会概念：帝国主义、封建主义、半殖民地等
- 不包括：普通名词（如"工人"、"农民"）

## 输出格式

返回 JSON 对象，包含 concepts 数组：

{
  "concepts": [
    {
      "name": "标准名称",
      "aliases": ["别名1"],
      "attributes": {
        "concept_type": "概念类型",
        "definition": "简短定义（可选）"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
他们反对以阶级斗争学说解释国民党的民生主义，他们反对国民党联俄和容纳共产党及左派分子。
```

输出：
```json
{
  "concepts": [
    {
      "name": "阶级斗争",
      "aliases": [],
      "attributes": {
        "concept_type": "政治概念"
      },
      "mentions": [
        {
          "line_start": 38,
          "line_end": 38,
          "context": "...他们反对以阶级斗争学说解释国民党的民生主义..."
        }
      ],
      "confidence": 1.0
    },
    {
      "name": "民生主义",
      "aliases": [],
      "attributes": {
        "concept_type": "政治概念"
      },
      "mentions": [
        {
          "line_start": 38,
          "line_end": 38,
          "context": "...他们反对以阶级斗争学说解释国民党的民生主义..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 7. 时间表达（Time Expression）抽取 Prompt

### System Message

```
你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取时间表达实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确的时间表达，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含文本位置信息（行号范围）
5. 必须包含上下文片段（前后各 20 字符）
```

### User Prompt 模板

```
请从以下文章中抽取所有时间表达实体。

## 实体定义

时间表达实体包括：
- 具体日期：一九二五年五月三十日
- 年份：一九二七年
- 月份：一九二五年五月
- 历史时期：第一次国内革命战争时期、抗日战争时期等
- 季节：一九二七年春
- 不包括：泛指的时间（如"现在"、"过去"）

## 输出格式

返回 JSON 对象，包含 time_expressions 数组：

{
  "time_expressions": [
    {
      "name": "原始表达",
      "attributes": {
        "time_type": "时间类型",
        "iso_format": "ISO格式（如可转换）"
      },
      "mentions": [
        {
          "line_start": 起始行号,
          "line_end": 结束行号,
          "context": "...上下文片段..."
        }
      ],
      "confidence": 0.0-1.0
    }
  ]
}

## 示例

输入文本：
```
一九二五年五月三十日，上海二千余学生分头在公共租界各马路进行宣传讲演。
```

输出：
```json
{
  "time_expressions": [
    {
      "name": "一九二五年五月三十日",
      "attributes": {
        "time_type": "具体日期",
        "iso_format": "1925-05-30"
      },
      "mentions": [
        {
          "line_start": 91,
          "line_end": 91,
          "context": "...一九二五年五月三十日，上海二千余学生分头在公共租界各马路进行宣传讲演..."
        }
      ],
      "confidence": 1.0
    }
  ]
}
```

## 待抽取文章

**卷册**: {volume_id}
**文章**: {article_title}
**日期**: {article_date}

**正文内容**:
{article_content}

请严格按照上述格式返回 JSON 结果。
```

## 批量抽取策略

### 1. 分批处理

- 每次 API 调用处理一篇文章
- 避免单次请求过长导致超时
- 便于错误恢复和增量更新

### 2. 错误处理

```python
def extract_with_retry(article, entity_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = call_deepseek_api(
                prompt=build_prompt(article, entity_type),
                system_message=get_system_message(entity_type)
            )
            return parse_result(result)
        except Exception as e:
            if attempt == max_retries - 1:
                log_error(article, entity_type, e)
                return None
            time.sleep(2 ** attempt)  # 指数退避
```

### 3. 成本控制

- 估算 token 消耗：每篇文章约 2000-5000 tokens
- 7 卷约 200-300 篇文章
- 7 种实体类型
- 总计约 1400-2100 次 API 调用
- 建议先对 volume-01 进行小规模测试

### 4. 质量控制

- 对 confidence < 0.8 的实体进行人工复核
- 定期抽查抽取结果
- 记录常见错误模式，优化 prompt

## 注意事项

1. **API 限流**: DeepSeek API 可能有速率限制，需要控制并发
2. **Token 限制**: 单次请求不超过模型的 context window
3. **JSON 解析**: 确保返回的 JSON 格式正确，处理解析错误
4. **增量更新**: 已抽取的文章不重复处理，除非 prompt 有重大更新
5. **日志记录**: 记录每次 API 调用的输入输出，便于调试和审计
