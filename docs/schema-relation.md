# 关系 Schema 规范

## 概述

本文档定义实体间关系的 schema。关系用于描述两个实体之间的语义连接，是构建知识图谱的核心。

## 关系 Schema

```json
{
  "relation_id": "string",
  "from_entity_id": "string",
  "from_entity_name": "string",
  "from_entity_type": "string",
  "to_entity_id": "string",
  "to_entity_name": "string",
  "to_entity_type": "string",
  "relation_type": "string",
  "confidence": "float",
  "evidence": [
    {
      "volume_id": "string",
      "article_id": "string",
      "article_title": "string",
      "line_start": "integer",
      "line_end": "integer",
      "context": "string"
    }
  ],
  "extracted_at": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

## 字段说明

- **relation_id**: 关系唯一标识符
  - 格式：`rel-{hash}`
  - 示例：`rel-a3f2c1b8`

- **from_entity_id**: 源实体 ID
  - 关系的起点
  - 示例：`person-mao-zedong`

- **from_entity_name**: 源实体名称
  - 冗余字段，便于查询
  - 示例：`毛泽东`

- **from_entity_type**: 源实体类型
  - 冗余字段，便于查询
  - 示例：`person`

- **to_entity_id**: 目标实体 ID
  - 关系的终点
  - 示例：`organization-ccp`

- **to_entity_name**: 目标实体名称
  - 冗余字段，便于查询
  - 示例：`中国共产党`

- **to_entity_type**: 目标实体类型
  - 冗余字段，便于查询
  - 示例：`organization`

- **relation_type**: 关系类型
  - 见下文关系类型定义
  - 示例：`member_of`、`participated_in`、`located_in`

- **confidence**: 置信度（0.0-1.0）
  - 由 LLM 抽取时给出
  - < 0.8 表示不确定，需要人工复核

- **evidence**: 支持证据列表
  - 至少包含一条证据
  - 每条证据包含文本位置和上下文

- **extracted_at**: 抽取时间戳（ISO 8601 格式）

- **created_at**: 创建时间戳

- **updated_at**: 更新时间戳

## 关系类型定义

### 人物相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `member_of` | 是...的成员 | 毛泽东 → 中国共产党 |
| `leader_of` | 是...的领导 | 毛泽东 → 中国共产党 |
| `participated_in` | 参与了... | 毛泽东 → 五卅运动 |
| `born_in` | 出生于... | 毛泽东 → 湖南湘潭 |
| `worked_in` | 工作于... | 毛泽东 → 湖南 |
| `authored` | 著作了... | 毛泽东 → 《矛盾论》 |
| `influenced_by` | 受...影响 | 毛泽东 → 马克思主义 |
| `colleague_of` | 是...的同事 | 毛泽东 → 周恩来 |
| `teacher_of` | 是...的老师 | 李大钊 → 毛泽东 |
| `student_of` | 是...的学生 | 毛泽东 → 李大钊 |

### 事件相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `occurred_in` | 发生于... | 五卅运动 → 上海 |
| `occurred_at` | 发生于...时间 | 五卅运动 → 1925年5月30日 |
| `led_by` | 由...领导 | 五卅运动 → 中国共产党 |
| `resulted_in` | 导致了... | 五卅运动 → 全国反帝高潮 |
| `part_of` | 是...的一部分 | 五卅运动 → 大革命时期 |

### 组织相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `founded_in` | 成立于... | 中国共产党 → 上海 |
| `founded_at` | 成立于...时间 | 中国共产党 → 1921年7月 |
| `headquartered_in` | 总部位于... | 中国共产党 → 上海 |
| `affiliated_with` | 隶属于... | 中国共产党 → 共产国际 |
| `opposed_to` | 反对... | 中国共产党 → 国民党右派 |
| `cooperated_with` | 合作于... | 中国共产党 → 国民党左派 |

### 地点相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `located_in` | 位于... | 湘潭 → 湖南 |
| `part_of` | 是...的一部分 | 湖南 → 中国 |
| `adjacent_to` | 邻近... | 湖南 → 湖北 |

### 著作相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `written_by` | 由...撰写 | 《矛盾论》 → 毛泽东 |
| `published_in` | 出版于... | 《矛盾论》 → 延安 |
| `published_at` | 出版于...时间 | 《矛盾论》 → 1937年8月 |
| `about` | 关于... | 《矛盾论》 → 辩证法 |
| `cites` | 引用了... | 《矛盾论》 → 《实践论》 |

### 概念相关关系

| 关系类型 | 说明 | 示例 |
|---------|------|------|
| `defined_by` | 由...定义 | 阶级斗争 → 马克思主义 |
| `related_to` | 相关于... | 阶级斗争 → 无产阶级 |
| `opposed_to` | 对立于... | 无产阶级 → 资产阶级 |
| `part_of` | 是...的一部分 | 阶级斗争 → 社会矛盾 |

## 示例

### 示例 1：人物-组织关系

```json
{
  "relation_id": "rel-mao-ccp-member",
  "from_entity_id": "person-mao-zedong",
  "from_entity_name": "毛泽东",
  "from_entity_type": "person",
  "to_entity_id": "organization-ccp",
  "to_entity_name": "中国共产党",
  "to_entity_type": "organization",
  "relation_type": "member_of",
  "confidence": 1.0,
  "evidence": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 74,
      "line_end": 74,
      "context": "...李大钊、谭平山、毛泽东、林伯渠、瞿秋白等共产党人参加了这次大会..."
    }
  ],
  "extracted_at": "2026-04-12T10:00:00Z",
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 示例 2：人物-事件关系

```json
{
  "relation_id": "rel-mao-wusa-participated",
  "from_entity_id": "person-mao-zedong",
  "from_entity_name": "毛泽东",
  "from_entity_type": "person",
  "to_entity_id": "event-wusa-movement",
  "to_entity_name": "五卅运动",
  "to_entity_type": "event",
  "relation_type": "participated_in",
  "confidence": 0.85,
  "evidence": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 40,
      "line_end": 40,
      "context": "...我们从一九二五年的五卅运动和各地农民运动的经验看来，这个断定是不错的..."
    }
  ],
  "extracted_at": "2026-04-12T10:00:00Z",
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 示例 3：事件-地点关系

```json
{
  "relation_id": "rel-wusa-shanghai-occurred",
  "from_entity_id": "event-wusa-movement",
  "from_entity_name": "五卅运动",
  "from_entity_type": "event",
  "to_entity_id": "place-shanghai",
  "to_entity_name": "上海",
  "to_entity_type": "place",
  "relation_type": "occurred_in",
  "confidence": 1.0,
  "evidence": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 90,
      "line_end": 92,
      "context": "...一九二五年五月间，上海、青岛的日本纱厂先后发生工人罢工的斗争...五月三十日，上海二千余学生分头在公共租界各马路进行宣传讲演..."
    }
  ],
  "extracted_at": "2026-04-12T10:00:00Z",
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

### 示例 4：人物-著作关系

```json
{
  "relation_id": "rel-mao-analysis-authored",
  "from_entity_id": "person-mao-zedong",
  "from_entity_name": "毛泽东",
  "from_entity_type": "person",
  "to_entity_id": "work-class-analysis",
  "to_entity_name": "中国社会各阶级的分析",
  "to_entity_type": "work",
  "relation_type": "authored",
  "confidence": 1.0,
  "evidence": [
    {
      "volume_id": "mao-volume-01",
      "article_id": "mao-volume-01-article-001",
      "article_title": "中国社会各阶级的分析",
      "line_start": 53,
      "line_end": 53,
      "context": "...毛泽东此文是为反对当时党内存在着的两种倾向而写的..."
    }
  ],
  "extracted_at": "2026-04-12T10:00:00Z",
  "created_at": "2026-04-12T10:00:00Z",
  "updated_at": "2026-04-12T10:00:00Z"
}
```

## 关系抽取原则

1. **证据充分**：每个关系必须有明确的文本证据支持
2. **类型准确**：选择最准确的关系类型，避免使用过于宽泛的类型
3. **方向明确**：注意关系的方向性（from → to）
4. **避免冗余**：同一对实体间的同类型关系只记录一次，但可以有多条证据
5. **置信度标注**：对于不确定的关系，诚实标注低置信度

## 关系去重与合并

当同一关系在多处出现时：
- 保持单一关系记录
- 合并所有证据到 `evidence` 列表
- 更新 `updated_at` 时间戳
- 置信度取最高值

## 输出格式

关系数据以 JSONL 格式存储在 `data/index/relations/relations.jsonl`，每行一个 JSON 对象。
