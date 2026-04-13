#!/usr/bin/env python3
"""
去重验证脚本

用于验证去重结果的正确性，生成指定人物的详细报告。

用法：
    python scripts/validate_deduplication.py --name 毛泽东
    python scripts/validate_deduplication.py --name 蒋介石 --show-mentions
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ENTITIES_DIR = PROJECT_ROOT / "data" / "index" / "entities"


def load_deduplicated_entity(name: str, entity_type: str = 'person') -> Optional[Dict]:
    """加载去重后的指定实体"""
    entity_file = ENTITIES_DIR / f"{entity_type}s.deduplicated.jsonl"

    if not entity_file.exists():
        print(f"错误：去重文件不存在: {entity_file}", file=sys.stderr)
        return None

    with open(entity_file, 'r', encoding='utf-8') as f:
        for line in f:
            entity = json.loads(line)
            if entity['name'] == name:
                return entity

    print(f"错误：未找到实体: {name}", file=sys.stderr)
    return None


def generate_entity_report(entity: Dict, show_mentions: bool = False):
    """生成实体详细报告"""
    print(f"\n{'='*60}")
    print(f"实体详细报告: {entity['name']}")
    print(f"{'='*60}\n")

    print(f"## 基本信息\n")
    print(f"- 名称: {entity['name']}")
    print(f"- 实体类型: {entity.get('entity_type', 'N/A')}")
    print(f"- 置信度: {entity.get('confidence', 'N/A')}")
    print(f"- 合并自: {entity.get('merged_from', 1)} 个实体")

    print(f"\n## 别名\n")
    aliases = entity.get('aliases', [])
    if aliases:
        for alias in aliases:
            print(f"  - {alias}")
    else:
        print("  (无)")

    print(f"\n## 属性\n")
    attributes = entity.get('attributes', {})

    roles = attributes.get('roles', [])
    print(f"### 角色 ({len(roles)})")
    if roles:
        for role in roles:
            print(f"  - {role}")
    else:
        print("  (无)")

    affiliations = attributes.get('affiliations', [])
    print(f"\n### 所属组织 ({len(affiliations)})")
    if affiliations:
        for affiliation in affiliations:
            print(f"  - {affiliation}")
    else:
        print("  (无)")

    print(f"\n## 来源信息\n")
    source_volumes = entity.get('source_volumes', [])
    print(f"- 来源卷册 ({len(source_volumes)}): {', '.join(source_volumes)}")

    merged_articles = entity.get('merged_articles', [])
    print(f"- 来源文章数: {len(merged_articles)}")

    mentions = entity.get('mentions', [])
    print(f"- 提及次数: {len(mentions)}")

    if show_mentions:
        print(f"\n## 所有提及\n")
        for i, mention in enumerate(mentions, 1):
            context = mention.get('context', '')
            # 截断过长的上下文
            if len(context) > 100:
                context = context[:100] + '...'
            print(f"{i}. {context}")

    print(f"\n## 来源文章列表\n")
    for article in merged_articles:
        print(f"  - {article}")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='去重验证脚本')
    parser.add_argument('--name', type=str, required=True, help='实体名称')
    parser.add_argument('--entity-type', type=str, default='person',
                        choices=['person', 'place', 'organization', 'event', 'work', 'concept'],
                        help='实体类型')
    parser.add_argument('--show-mentions', action='store_true',
                        help='显示所有提及的上下文')

    args = parser.parse_args()

    # 加载实体
    entity = load_deduplicated_entity(args.name, args.entity_type)
    if not entity:
        sys.exit(1)

    # 生成报告
    generate_entity_report(entity, args.show_mentions)


if __name__ == '__main__':
    main()
