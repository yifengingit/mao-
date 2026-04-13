# 实体 Schema 规范

## 概述

本文档定义 Phase 2 结构化抽取中使用的实体 schema。所有实体类型共享统一的基础结构，并根据类型添加特定属性。

## 实体类型

支持 7 种实体类型：

1. **person** - 人物
2. **event** - 事件
3. **organization** - 组织
4. **place** - 地点
5. **work** - 著作
6. **concept** - 概念
7. **time_expression** - 时间表达

## 通用 Schema

所有实体类型共享以下字段：

```json
{
  "entity_id": "string",
  "entity_type": "person|event|organization|place|work|concept|time_expression",
  "name": "string",
  "aliases": ["string"],
  "mentions": [
    {
      "volume_id": "string",
      "article_id": "string",
      "article_title": "string",
      "line_start": "integer",
      "line_end": "integer",
      "context": "string"
    }
  ],
  "attributes": {},
  "source_volumes": ["string"],
  "confidence": "float",
  "created_at": "string",
  "updated_at": "string"
}
```

### 字段说明

- **entity_id**: 全局唯一标识符
  - 格式：`{type}-{hash}`
  - 示例：`person-a3f2c1b8`、`event-9d4e7f2a`
  - 使用内容哈希确保同名实体可区分

- **entity_type**: 实体类型枚举值

- **name**: 标准名称
  - 使用最常见或最正式的名称
  - 示例：`毛泽东`、`五卅运动`、`中国共产党`

- **aliases**: 别名列表
  - 包含所有在文本中出现的变体
  - 示例：`["毛主席", "润之"]`、`["中共", "共产党"]`

- **mentions**: 在文本中的所有出现位置
  - `volume_id`: 卷册 ID（如 `mao-volume-01`）
  - `article_id`: 文章 ID（如 `mao-volume-01-article-001`）
  - `article_title`: 文章标题
  - `line_start`: 起始行号
  - `line_end`: 结束行号
  - `context`: 上下文片段（前后各 50 字符）

- **attributes**: 类型特定属性（见下文各类型定义）

- **source_volumes**: 来源卷册列表
  - 自动从 mentions 聚合
  - 示例：`["mao-volume-01", "mao-volume-02"]`

- **confidence**: 置信度（0.0-1.0）
  - 由 LLM 抽取时给出
  - < 0.8 表示不确定，需要人工复核

- **created_at**: 创建时间戳（ISO 8601 格式）

- **updated_at**: 更新时间戳（ISO 8601 格式）

## 类型特定属性

### 1. person（人物）

```json
{
  "attributes": {
    "birth_year": "string",
    "death_year": "string",
    "birth_place": "string",
    "roles": ["string"],
    "affiliations": ["string"]
  }
}
```

**字段说明**：
- `birth_year`: 出生年份（如 `1893`）
- `death_year`: 逝世年份（如 `1976`）
- `birth_place`: 出生地（如 `湖南湘潭`）
- `roles`: 角色列表（如 `["革命家", "政治家", "军事家"]`）
- `affiliations`: 所属组织（如 `["中国共产党", "中华人民共和国"]`）

**示例**：
```json
{
  "entity_id": "person-mao-zedong",
  "entity_type": "person",
  "name": "毛泽东",
  "aliases": ["毛主席", "润之"],
  "attributes": {
    "birth_year": "1893",
    "death_year": "1976",
    "birth_place": "湖南湘潭",
    "roles": ["革命家", "政治家", "军事家", "思想家"],
    "affiliations": ["中国共产党", "中华人民共和国"]
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 53,
      "line_end": 53,
      "context": "...毛泽东此文是为反对当时党内存在着的两种倾向而写的..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 1.0,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 2. event（事件）

```json
{
  "attributes": {
    "start_date": "string",
    "end_date": "string",
    "location": "string",
    "participants": ["string"],
    "event_type": "string"
  }
}
```

**字段说明**：
- `start_date`: 开始日期（ISO 8601 格式，如 `1925-05-30`）
- `end_date`: 结束日期（可选）
- `location`: 发生地点
- `participants`: 参与者列表
- `event_type`: 事件类型（如 `运动`、`会议`、`战役`、`罢工`）

**示例**：
```json
{
  "entity_id": "event-wusa-movement",
  "entity_type": "event",
  "name": "五卅运动",
  "aliases": ["五卅惨案", "五卅反帝爱国运动"],
  "attributes": {
    "start_date": "1925-05-30",
    "end_date": "1925-06-30",
    "location": "上海",
    "participants": ["工人", "学生", "市民"],
    "event_type": "反帝爱国运动"
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 40,
      "line_end": 40,
      "context": "...我们从一九二五年的五卅运动和各地农民运动的经验看来..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 0.95,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 3. organization（组织）

```json
{
  "attributes": {
    "founded_date": "string",
    "dissolved_date": "string",
    "organization_type": "string",
    "headquarters": "string",
    "leaders": ["string"]
  }
}
```

**字段说明**：
- `founded_date`: 成立日期
- `dissolved_date`: 解散日期（可选）
- `organization_type`: 组织类型（如 `政党`、`团体`、`机构`）
- `headquarters`: 总部所在地
- `leaders`: 领导人列表

**示例**：
```json
{
  "entity_id": "organization-ccp",
  "entity_type": "organization",
  "name": "中国共产党",
  "aliases": ["中共", "共产党"],
  "attributes": {
    "founded_date": "1921-07-23",
    "organization_type": "政党",
    "headquarters": "上海",
    "leaders": ["陈独秀", "毛泽东"]
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 74,
      "line_end": 74,
      "context": "...一九二二年中国共产党参加共产国际..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 1.0,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 4. place（地点）

```json
{
  "attributes": {
    "place_type": "string",
    "parent_place": "string",
    "coordinates": {
      "latitude": "float",
      "longitude": "float"
    },
    "historical_names": ["string"]
  }
}
```

**字段说明**：
- `place_type`: 地点类型（如 `国家`、`省份`、`城市`、`县`、`村`）
- `parent_place`: 上级行政区划
- `coordinates`: 地理坐标（可选）
- `historical_names`: 历史名称列表

**示例**：
```json
{
  "entity_id": "place-hunan",
  "entity_type": "place",
  "name": "湖南",
  "aliases": ["湖南省", "湘"],
  "attributes": {
    "place_type": "省份",
    "parent_place": "中国",
    "historical_names": []
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-002",
      "article_title": "湖南农民运动考察报告",
      "line_start": 100,
      "line_end": 100,
      "context": "...湖南的农民运动..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 1.0,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 5. work（著作）

```json
{
  "attributes": {
    "author": "string",
    "publication_date": "string",
    "work_type": "string",
    "publisher": "string"
  }
}
```

**字段说明**：
- `author`: 作者
- `publication_date`: 出版日期
- `work_type`: 著作类型（如 `书籍`、`文章`、`报刊`、`演讲`）
- `publisher`: 出版者

**示例**：
```json
{
  "entity_id": "work-chenbo",
  "entity_type": "work",
  "name": "晨报",
  "aliases": ["北京晨报", "《晨报》"],
  "attributes": {
    "author": "",
    "publication_date": "1918-12",
    "work_type": "报刊",
    "publisher": "北京"
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 68,
      "line_end": 68,
      "context": "...在北京《晨报》上发表议论..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 0.9,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 6. concept（概念）

```json
{
  "attributes": {
    "concept_type": "string",
    "definition": "string",
    "related_concepts": ["string"]
  }
}
```

**字段说明**：
- `concept_type`: 概念类型（如 `政治理论`、`经济术语`、`军事概念`）
- `definition`: 定义或解释
- `related_concepts`: 相关概念列表

**示例**：
```json
{
  "entity_id": "concept-class-struggle",
  "entity_type": "concept",
  "name": "阶级斗争",
  "aliases": ["阶级斗争学说"],
  "attributes": {
    "concept_type": "政治理论",
    "definition": "不同阶级之间因经济利益冲突而产生的对抗",
    "related_concepts": ["阶级", "无产阶级", "资产阶级"]
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 38,
      "line_end": 38,
      "context": "...他们反对以阶级斗争学说解释国民党的民生主义..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 0.85,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 7. time_expression（时间表达）

```json
{
  "attributes": {
    "normalized_date": "string",
    "date_type": "string",
    "precision": "string"
  }
}
```

**字段说明**：
- `normalized_date`: 标准化日期（ISO 8601 格式）
- `date_type`: 日期类型（如 `具体日期`、`年份`、`时期`）
- `precision`: 精度（如 `day`、`month`、`year`、`decade`）

**示例**：
```json
{
  "entity_id": "time-19250530",
  "entity_type": "time_expression",
  "name": "一九二五年五月三十日",
  "aliases": ["1925年5月30日"],
  "attributes": {
    "normalized_date": "1925-05-30",
    "date_type": "具体日期",
    "precision": "day"
  },
  "mentions": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 89,
      "line_end": 89,
      "context": "...指一九二五年五月三十日爆发的反帝爱国运动..."
    }
  ],
  "source_volumes": ["mao-volume-01"],
  "confidence": 1.0,
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

## 存储格式

实体以 JSONL 格式存储，每种类型一个文件：

- `data/index/entities/persons.jsonl`
- `data/index/entities/events.jsonl`
- `data/index/entities/organizations.jsonl`
- `data/index/entities/places.jsonl`
- `data/index/entities/works.jsonl`
- `data/index/entities/concepts.jsonl`
- `data/index/entities/time_expressions.jsonl`

每行一个 JSON 对象，便于流式处理和增量更新。

## 实体去重与合并

当同一实体在多篇文章中出现时：

1. 使用 `name` 和 `entity_type` 进行初步匹配
2. 检查 `aliases` 是否有交集
3. 合并 `mentions` 列表
4. 更新 `source_volumes` 列表
5. 保留置信度最高的 `attributes`
6. 更新 `updated_at` 时间戳

## 质量控制

- `confidence < 0.8` 的实体需要人工复核
- 每个实体至少有 1 个 mention
- `mentions` 中的 `line_start` 和 `line_end` 必须有效
- `attributes` 中的日期必须符合 ISO 8601 格式
