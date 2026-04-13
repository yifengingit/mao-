# 档案 Schema 规范

## 概述

档案是实体的聚合视图，将分散在多篇文章中的同一实体信息整合为统一的档案页面。档案包含实体基础信息、关联实体、时间线、引用文献和摘要描述。

## 档案类型

支持 5 种档案类型：

1. **person_archive** - 人物档案
2. **event_archive** - 事件档案
3. **organization_archive** - 组织档案
4. **place_archive** - 地点档案
5. **work_archive** - 著作档案

注：概念（concept）和时间表达（time_expression）暂不生成独立档案。

## 通用 Schema

所有档案类型共享以下基础结构：

```json
{
  "archive_id": "string",
  "archive_type": "person_archive|event_archive|organization_archive|place_archive|work_archive",
  "entity_id": "string",
  "name": "string",
  "aliases": ["string"],
  "summary": "string",
  "attributes": {},
  "related_entities": {
    "persons": [],
    "events": [],
    "organizations": [],
    "places": [],
    "works": [],
    "concepts": []
  },
  "timeline": [],
  "references": [],
  "statistics": {},
  "created_at": "string",
  "updated_at": "string"
}
```

### 字段说明

- **archive_id**: 档案唯一标识符
  - 格式：`archive-{entity_id}`
  - 示例：`archive-person-mao-zedong`

- **archive_type**: 档案类型枚举值

- **entity_id**: 对应实体的 ID

- **name**: 实体标准名称

- **aliases**: 实体别名列表

- **summary**: 档案摘要
  - 由 LLM 生成的简短描述（200-500 字）
  - 概括实体的核心信息和历史意义

- **attributes**: 从实体继承的类型特定属性

- **related_entities**: 关联实体
  - 按类型分组的相关实体列表
  - 每个实体包含 `entity_id`、`name`、`relation_type`

- **timeline**: 时间线
  - 按时间排序的关键事件列表
  - 每个事件包含日期、描述、来源

- **references**: 引用文献
  - 该实体在原文中的所有出现位置
  - 按卷册和文章组织

- **statistics**: 统计信息
  - 出现次数、关联实体数量等

- **created_at**: 创建时间戳

- **updated_at**: 更新时间戳

## 类型特定 Schema

### 1. person_archive（人物档案）

```json
{
  "archive_type": "person_archive",
  "attributes": {
    "birth_year": "string",
    "death_year": "string",
    "birth_place": "string",
    "roles": ["string"],
    "affiliations": ["string"]
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "colleague_of|teacher_of|student_of"
      }
    ],
    "events": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "participated_in|led"
      }
    ],
    "organizations": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "member_of|leader_of|founded"
      }
    ],
    "places": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "born_in|worked_in|lived_in"
      }
    ],
    "works": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "authored"
      }
    ],
    "concepts": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "advocated|developed"
      }
    ]
  },
  "timeline": [
    {
      "date": "string",
      "event": "string",
      "source": {
        "volume_id": "string",
        "article_id": "string",
        "article_title": "string"
      }
    }
  ]
}
```

**示例**：
```json
{
  "archive_id": "archive-person-mao-zedong",
  "archive_type": "person_archive",
  "entity_id": "person-mao-zedong",
  "name": "毛泽东",
  "aliases": ["毛主席", "润之"],
  "summary": "毛泽东（1893-1976），字润之，湖南湘潭人。中国共产党、中国人民解放军和中华人民共和国的主要缔造者和领导人，马克思主义中国化的伟大开拓者，毛泽东思想的主要创立者。",
  "attributes": {
    "birth_year": "1893",
    "death_year": "1976",
    "birth_place": "湖南湘潭",
    "roles": ["革命家", "政治家", "军事家", "思想家"],
    "affiliations": ["中国共产党", "中华人民共和国"]
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "person-zhou-enlai",
        "name": "周恩来",
        "relation_type": "colleague_of"
      },
      {
        "entity_id": "person-li-dazhao",
        "name": "李大钊",
        "relation_type": "teacher_of"
      }
    ],
    "events": [
      {
        "entity_id": "event-wusa-movement",
        "name": "五卅运动",
        "relation_type": "participated_in"
      }
    ],
    "organizations": [
      {
        "entity_id": "organization-ccp",
        "name": "中国共产党",
        "relation_type": "member_of"
      }
    ],
    "places": [
      {
        "entity_id": "place-hunan",
        "name": "湖南",
        "relation_type": "born_in"
      }
    ],
    "works": [
      {
        "entity_id": "work-class-analysis",
        "name": "中国社会各阶级的分析",
        "relation_type": "authored"
      }
    ],
    "concepts": [
      {
        "entity_id": "concept-class-struggle",
        "name": "阶级斗争",
        "relation_type": "advocated"
      }
    ]
  },
  "timeline": [
    {
      "date": "1893-12-26",
      "event": "出生于湖南湘潭",
      "source": {
        "volume_id": "mao-volume-01",
        "article_id": "mao-volume-01-article-000",
        "article_title": "第一卷第二版出版说明"
      }
    },
    {
      "date": "1925-12-01",
      "event": "撰写《中国社会各阶级的分析》",
      "source": {
        "volume_id": "mao-volume-01",
        "article_id": "mao-volume-01-article-001",
        "article_title": "中国社会各阶级的分析"
      }
    }
  ],
  "references": [
    {
      "volume_id": "mao-volume-01",
      "volume_title": "毛泽东选集第一卷",
      "articles": [
        {
          "article_id": "mao-volume-01-article-001",
          "article_title": "中国社会各阶级的分析",
          "mention_count": 3
        }
      ]
    }
  ],
  "statistics": {
    "total_mentions": 15,
    "total_articles": 8,
    "total_volumes": 3,
    "related_persons": 5,
    "related_events": 10,
    "related_organizations": 3
  },
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 2. event_archive（事件档案）

```json
{
  "archive_type": "event_archive",
  "attributes": {
    "start_date": "string",
    "end_date": "string",
    "location": "string",
    "participants": ["string"],
    "event_type": "string"
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "participated_in|led"
      }
    ],
    "organizations": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "organized_by|participated_in"
      }
    ],
    "places": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "occurred_in"
      }
    ],
    "events": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "led_to|part_of|preceded_by"
      }
    ]
  }
}
```

**示例**：
```json
{
  "archive_id": "archive-event-wusa-movement",
  "archive_type": "event_archive",
  "entity_id": "event-wusa-movement",
  "name": "五卅运动",
  "aliases": ["五卅惨案", "五卅反帝爱国运动"],
  "summary": "五卅运动是1925年5月30日在上海爆发的反帝爱国运动。起因是日本资本家枪杀工人顾正红，英帝国主义巡捕向抗议群众开枪，造成重大伤亡。此事件激起全国人民公愤，形成全国规模的反帝爱国运动高潮。",
  "attributes": {
    "start_date": "1925-05-30",
    "end_date": "1925-06-30",
    "location": "上海",
    "participants": ["工人", "学生", "市民"],
    "event_type": "反帝爱国运动"
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "person-gu-zhenghong",
        "name": "顾正红",
        "relation_type": "victim"
      }
    ],
    "organizations": [
      {
        "entity_id": "organization-ccp",
        "name": "中国共产党",
        "relation_type": "organized_by"
      }
    ],
    "places": [
      {
        "entity_id": "place-shanghai",
        "name": "上海",
        "relation_type": "occurred_in"
      }
    ],
    "events": [
      {
        "entity_id": "event-northern-expedition",
        "name": "北伐战争",
        "relation_type": "led_to"
      }
    ]
  },
  "timeline": [
    {
      "date": "1925-05-15",
      "event": "日本资本家枪杀工人顾正红",
      "source": {
        "volume_id": "mao-volume-01",
        "article_id": "mao-volume-01-article-001",
        "article_title": "中国社会各阶级的分析"
      }
    },
    {
      "date": "1925-05-30",
      "event": "英帝国主义巡捕向群众开枪，造成五卅惨案",
      "source": {
        "volume_id": "mao-volume-01",
        "article_id": "mao-volume-01-article-001",
        "article_title": "中国社会各阶级的分析"
      }
    }
  ],
  "references": [
    {
      "volume_id": "mao-volume-01",
      "volume_title": "毛泽东选集第一卷",
      "articles": [
        {
          "article_id": "mao-volume-01-article-001",
          "article_title": "中国社会各阶级的分析",
          "mention_count": 2
        }
      ]
    }
  ],
  "statistics": {
    "total_mentions": 5,
    "total_articles": 3,
    "total_volumes": 2,
    "related_persons": 2,
    "related_organizations": 1,
    "related_places": 2
  },
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 3. organization_archive（组织档案）

```json
{
  "archive_type": "organization_archive",
  "attributes": {
    "founded_date": "string",
    "dissolved_date": "string",
    "organization_type": "string",
    "headquarters": "string",
    "leaders": ["string"]
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "member_of|leader_of|founder_of"
      }
    ],
    "events": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "organized|participated_in"
      }
    ],
    "organizations": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "affiliated_with|opposed_to|cooperated_with"
      }
    ],
    "places": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "founded_in|headquartered_in"
      }
    ]
  }
}
```

### 4. place_archive（地点档案）

```json
{
  "archive_type": "place_archive",
  "attributes": {
    "place_type": "string",
    "parent_place": "string",
    "coordinates": {
      "latitude": "float",
      "longitude": "float"
    },
    "historical_names": ["string"]
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "born_in|worked_in|lived_in"
      }
    ],
    "events": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "occurred_in"
      }
    ],
    "organizations": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "founded_in|headquartered_in"
      }
    ],
    "places": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "part_of|adjacent_to"
      }
    ]
  }
}
```

### 5. work_archive（著作档案）

```json
{
  "archive_type": "work_archive",
  "attributes": {
    "author": "string",
    "publication_date": "string",
    "work_type": "string",
    "publisher": "string"
  },
  "related_entities": {
    "persons": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "authored|edited"
      }
    ],
    "concepts": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "discusses|defines"
      }
    ],
    "works": [
      {
        "entity_id": "string",
        "name": "string",
        "relation_type": "cites|cited_by"
      }
    ]
  }
}
```

## 档案生成流程

1. **实体聚合**：从 `entities/*.jsonl` 读取所有实体
2. **关系聚合**：从 `relations/relations.jsonl` 读取相关关系
3. **时间线构建**：从实体 mentions 和关系 evidence 提取时间信息
4. **摘要生成**：调用 LLM 生成档案摘要
5. **统计计算**：计算出现次数、关联实体数量等
6. **输出档案**：写入 `archives/{type}/{archive_id}.json`

## 存储格式

档案使用 JSON 格式（非 JSONL），每个档案一个独立文件：

```
data/index/archives/
├── person_archives/
│   ├── archive-person-mao-zedong.json
│   └── archive-person-zhou-enlai.json
├── event_archives/
│   └── archive-event-wusa-movement.json
├── organization_archives/
│   └── archive-organization-ccp.json
├── place_archives/
│   └── archive-place-hunan.json
└── work_archives/
    └── archive-work-class-analysis.json
```

## 使用场景

- **知识浏览**：为网站提供实体详情页
- **关系探索**：展示实体间的关联网络
- **时间线可视化**：按时间顺序展示实体相关事件
- **引用回溯**：快速定位实体在原文中的位置
- **统计分析**：了解实体的重要程度和影响范围
