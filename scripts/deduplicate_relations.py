#!/usr/bin/env python3
"""
关系去重脚本

将同一关系的多次出现合并为单一关系，聚合所有证据。

用法：
    python scripts/deduplicate_relations.py
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
RELATIONS_DIR = PROJECT_ROOT / "data" / "index" / "relations"


def load_relations() -> List[Dict]:
    """加载关系文件"""
    relations_file = RELATIONS_DIR / "relations.jsonl"

    if not relations_file.exists():
        print(f"错误：关系文件不存在: {relations_file}", file=sys.stderr)
        sys.exit(1)

    relations = []
    with open(relations_file, 'r', encoding='utf-8') as f:
        for line in f:
            relations.append(json.loads(line))

    return relations


def merge_relations(relations: List[Dict]) -> Dict:
    """合并同一关系的多次出现"""
    if len(relations) == 1:
        return relations[0]

    base = relations[0].copy()

    # 合并 evidence
    all_evidence = []
    for relation in relations:
        all_evidence.extend(relation.get('evidence', []))
    base['evidence'] = all_evidence

    # 平均 confidence
    confidences = [r.get('confidence', 1.0) for r in relations]
    avg_confidence = sum(confidences) / len(confidences)
    base['confidence'] = round(avg_confidence, 2)

    # 记录合并信息
    base['merged_from'] = len(relations)
    base['merged_articles'] = sorted(list(set(
        e['article_id'] for r in relations for e in r.get('evidence', [])
    )))

    return base


def deduplicate_relations(relations: List[Dict]) -> tuple[List[Dict], Dict]:
    """去重关系，返回去重后的关系列表和统计信息"""
    # 按 (from_entity_name, to_entity_name, relation_type) 分组
    relation_groups = defaultdict(list)

    for relation in relations:
        key = (
            relation['from_entity_name'],
            relation['to_entity_name'],
            relation['relation_type']
        )
        relation_groups[key].append(relation)

    # 合并每组
    deduplicated = []
    merge_stats = {}

    for key, group in relation_groups.items():
        merged = merge_relations(group)
        deduplicated.append(merged)

        if len(group) > 1:
            from_name, to_name, rel_type = key
            merge_stats[f"{from_name} --[{rel_type}]--> {to_name}"] = {
                'count': len(group),
                'evidence_count': len(merged['evidence']),
                'articles': merged['merged_articles']
            }

    # 统计信息
    stats = {
        'original_count': len(relations),
        'deduplicated_count': len(deduplicated),
        'merged_count': len(relations) - len(deduplicated),
        'unique_relations': len(relation_groups),
        'duplicated_relations': len(merge_stats),
        'merge_details': merge_stats
    }

    return deduplicated, stats


def save_deduplicated_relations(relations: List[Dict]):
    """保存去重后的关系"""
    output_file = RELATIONS_DIR / "relations.deduplicated.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        for relation in relations:
            f.write(json.dumps(relation, ensure_ascii=False) + '\n')

    print(f"去重后的关系已保存到: {output_file}")


def generate_report(stats: Dict):
    """生成去重报告"""
    report_file = RELATIONS_DIR / "deduplication-report.md"

    # 按合并次数排序
    top_merged = sorted(
        stats['merge_details'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]

    report = f"""# 关系去重报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计摘要

- **去重前关系数**: {stats['original_count']}
- **去重后关系数**: {stats['deduplicated_count']}
- **合并的关系数**: {stats['merged_count']}
- **唯一关系数**: {stats['unique_relations']}
- **有重复的关系数**: {stats['duplicated_relations']}

## 合并率

- **去重率**: {stats['merged_count'] / stats['original_count'] * 100:.1f}%
- **平均每个关系的出现次数**: {stats['original_count'] / stats['unique_relations']:.2f}

## 前 20 个合并次数最多的关系

| 排名 | 关系 | 合并次数 | 证据数 | 来源文章数 |
|------|------|----------|--------|------------|
"""

    for i, (relation, detail) in enumerate(top_merged, 1):
        report += f"| {i} | {relation} | {detail['count']} | {detail['evidence_count']} | {len(detail['articles'])} |\n"

    report += f"""

## 合并详情

以下是所有有重复的关系的详细信息：

"""

    for relation, detail in sorted(stats['merge_details'].items(), key=lambda x: x[1]['count'], reverse=True):
        report += f"### {relation}\n\n"
        report += f"- **合并次数**: {detail['count']}\n"
        report += f"- **证据数**: {detail['evidence_count']}\n"
        report += f"- **来源文章数**: {len(detail['articles'])}\n"
        report += f"- **来源文章**: \n"
        for article in detail['articles']:
            report += f"  - {article}\n"
        report += "\n"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"去重报告已保存到: {report_file}")


def main():
    print("开始去重关系...")

    # 加载关系
    relations = load_relations()
    print(f"已加载 {len(relations)} 个关系")

    # 去重
    deduplicated, stats = deduplicate_relations(relations)
    print(f"去重完成：{stats['original_count']} -> {stats['deduplicated_count']}")
    print(f"合并了 {stats['merged_count']} 个重复关系")

    # 保存去重后的关系
    save_deduplicated_relations(deduplicated)

    # 生成报告
    generate_report(stats)

    print("\n去重完成！")
    print(f"- 去重前: {stats['original_count']} 个关系")
    print(f"- 去重后: {stats['deduplicated_count']} 个关系")
    print(f"- 去重率: {stats['merged_count'] / stats['original_count'] * 100:.1f}%")


if __name__ == '__main__':
    main()
