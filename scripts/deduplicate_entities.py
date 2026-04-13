#!/usr/bin/env python3
"""
实体去重脚本

将同名实体合并为单一实体，聚合所有 mentions 和属性。

用法：
    python scripts/deduplicate_entities.py --entity-type person
    python scripts/deduplicate_entities.py --entity-type place
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ENTITIES_DIR = PROJECT_ROOT / "data" / "index" / "entities"


def load_entities(entity_type: str) -> List[Dict]:
    """加载实体文件"""
    entity_file = ENTITIES_DIR / f"{entity_type}s.jsonl"

    if not entity_file.exists():
        print(f"错误：实体文件不存在: {entity_file}", file=sys.stderr)
        sys.exit(1)

    entities = []
    with open(entity_file, 'r', encoding='utf-8') as f:
        for line in f:
            entities.append(json.loads(line))

    return entities


def merge_entities(entities: List[Dict]) -> Dict:
    """合并同名实体"""
    if len(entities) == 1:
        return entities[0]

    base = entities[0].copy()

    # 合并 mentions
    all_mentions = []
    for entity in entities:
        all_mentions.extend(entity.get('mentions', []))
    base['mentions'] = all_mentions

    # 合并 aliases
    all_aliases = set(base.get('aliases', []))
    for entity in entities[1:]:
        all_aliases.update(entity.get('aliases', []))
    base['aliases'] = sorted(list(all_aliases))

    # 合并 attributes
    if 'attributes' not in base:
        base['attributes'] = {}

    # 合并 roles
    all_roles = set(base.get('attributes', {}).get('roles', []))
    for entity in entities[1:]:
        all_roles.update(entity.get('attributes', {}).get('roles', []))
    if all_roles:
        base['attributes']['roles'] = sorted(list(all_roles))

    # 合并 affiliations（人物专用）
    all_affiliations = set(base.get('attributes', {}).get('affiliations', []))
    for entity in entities[1:]:
        all_affiliations.update(entity.get('attributes', {}).get('affiliations', []))
    if all_affiliations:
        base['attributes']['affiliations'] = sorted(list(all_affiliations))

    # 合并 place_type（地点专用，取第一个非空值）
    if not base['attributes'].get('place_type'):
        for entity in entities[1:]:
            pt = entity.get('attributes', {}).get('place_type')
            if pt:
                base['attributes']['place_type'] = pt
                break

    # 合并 modern_name（地点专用，收集所有不同的现代名称）
    modern_names = set()
    for entity in entities:
        mn = entity.get('attributes', {}).get('modern_name')
        if mn:
            modern_names.add(mn)
    if modern_names:
        # 只有一个就直接用字符串，多个用列表
        base['attributes']['modern_name'] = (
            list(modern_names)[0] if len(modern_names) == 1 else sorted(list(modern_names))
        )

    # 合并 source_volumes
    all_volumes = set()
    for entity in entities:
        # 兼容旧格式（source_volume）和新格式（source_volumes）
        if 'source_volumes' in entity:
            all_volumes.update(entity['source_volumes'])
        elif 'source_volume' in entity:
            all_volumes.add(entity['source_volume'])
    base['source_volumes'] = sorted(list(all_volumes))

    # 移除旧的 source_volume 字段
    if 'source_volume' in base:
        del base['source_volume']

    # 平均 confidence
    confidences = [e.get('confidence', 1.0) for e in entities]
    avg_confidence = sum(confidences) / len(confidences)
    base['confidence'] = round(avg_confidence, 2)

    # 记录合并信息
    base['merged_from'] = len(entities)
    base['merged_articles'] = sorted(list(set(e['source_article'] for e in entities)))

    return base


def deduplicate_entities(entities: List[Dict]) -> tuple[List[Dict], Dict]:
    """去重实体，返回去重后的实体列表和统计信息"""
    # 按 name 分组
    name_groups = defaultdict(list)
    for entity in entities:
        name = entity['name']
        name_groups[name].append(entity)

    # 合并每组
    deduplicated = []
    merge_stats = {}

    for name, group in name_groups.items():
        merged = merge_entities(group)
        deduplicated.append(merged)

        if len(group) > 1:
            merge_stats[name] = {
                'count': len(group),
                'articles': merged['merged_articles'],
                'mentions': len(merged['mentions']),
                'volumes': merged['source_volumes']
            }

    # 统计信息
    stats = {
        'original_count': len(entities),
        'deduplicated_count': len(deduplicated),
        'merged_count': len(entities) - len(deduplicated),
        'unique_names': len(name_groups),
        'duplicated_names': len(merge_stats),
        'merge_details': merge_stats
    }

    return deduplicated, stats


def save_deduplicated_entities(entities: List[Dict], entity_type: str):
    """保存去重后的实体"""
    output_file = ENTITIES_DIR / f"{entity_type}s.deduplicated.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        for entity in entities:
            f.write(json.dumps(entity, ensure_ascii=False) + '\n')

    print(f"去重后的实体已保存到: {output_file}")


def generate_report(stats: Dict, entity_type: str):
    """生成去重报告"""
    report_file = ENTITIES_DIR / f"deduplication-report-{entity_type}.md"

    # 按合并次数排序
    top_merged = sorted(
        stats['merge_details'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]

    report = f"""# 实体去重报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计摘要

- **实体类型**: {entity_type}
- **去重前实体数**: {stats['original_count']}
- **去重后实体数**: {stats['deduplicated_count']}
- **合并的实体数**: {stats['merged_count']}
- **唯一名称数**: {stats['unique_names']}
- **有重复的名称数**: {stats['duplicated_names']}

## 合并率

- **去重率**: {stats['merged_count'] / stats['original_count'] * 100:.1f}%
- **平均每个名称的实体数**: {stats['original_count'] / stats['unique_names']:.2f}

## 前 20 个合并次数最多的实体

| 排名 | 名称 | 合并次数 | 提及次数 | 来源卷册 | 来源文章数 |
|------|------|----------|----------|----------|------------|
"""

    for i, (name, detail) in enumerate(top_merged, 1):
        volumes = ', '.join(detail['volumes'])
        report += f"| {i} | {name} | {detail['count']} | {detail['mentions']} | {volumes} | {len(detail['articles'])} |\n"

    report += f"""

## 合并详情

以下是所有有重复的实体的详细信息：

"""

    for name, detail in sorted(stats['merge_details'].items(), key=lambda x: x[1]['count'], reverse=True):
        report += f"### {name}\n\n"
        report += f"- **合并次数**: {detail['count']}\n"
        report += f"- **提及次数**: {detail['mentions']}\n"
        report += f"- **来源卷册**: {', '.join(detail['volumes'])}\n"
        report += f"- **来源文章数**: {len(detail['articles'])}\n"
        report += f"- **来源文章**: \n"
        for article in detail['articles']:
            report += f"  - {article}\n"
        report += "\n"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"去重报告已保存到: {report_file}")


def main():
    parser = argparse.ArgumentParser(description='实体去重脚本')
    parser.add_argument('--entity-type', required=True, choices=['person', 'place', 'organization', 'event', 'work', 'concept', 'time_expression'],
                        help='实体类型')

    args = parser.parse_args()

    print(f"开始去重 {args.entity_type} 实体...")

    # 加载实体
    entities = load_entities(args.entity_type)
    print(f"加载了 {len(entities)} 个实体")

    # 去重
    deduplicated, stats = deduplicate_entities(entities)
    print(f"去重后剩余 {len(deduplicated)} 个实体")
    print(f"合并了 {stats['merged_count']} 个重复实体")

    # 保存去重后的实体
    save_deduplicated_entities(deduplicated, args.entity_type)

    # 生成报告
    generate_report(stats, args.entity_type)

    print("\n去重完成！")
    print(f"- 去重前: {stats['original_count']} 个实体")
    print(f"- 去重后: {stats['deduplicated_count']} 个实体")
    print(f"- 去重率: {stats['merged_count'] / stats['original_count'] * 100:.1f}%")


if __name__ == '__main__':
    main()
