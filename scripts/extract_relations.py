#!/usr/bin/env python3
"""
关系抽取脚本

从文章中抽取人物间的关系。

用法：
    python scripts/extract_relations.py --article mao-volume-01-article-001
    python scripts/extract_relations.py --volume mao-volume-01
    python scripts/extract_relations.py --all
"""

import argparse
import json
import os
import sys
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import requests


# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = PROJECT_ROOT / "data" / "index" / "articles"
ENTITIES_DIR = PROJECT_ROOT / "data" / "index" / "entities"
RELATIONS_DIR = PROJECT_ROOT / "data" / "index" / "relations"
CLEANED_DIR = PROJECT_ROOT / "data" / "clean" / "volumes"


def call_deepseek_api(system_message: str, user_prompt: str, temperature: float = 0.1, max_retries: int = 3) -> Optional[Dict]:
    """调用 DeepSeek API，支持重试"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"错误：API 返回格式异常: {result}", file=sys.stderr)
                return None

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"  API 超时，{wait_time} 秒后重试（第 {attempt + 1}/{max_retries - 1} 次重试）...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                print(f"错误：API 调用超时，已重试 {max_retries} 次", file=sys.stderr)
                return None

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"  API 调用失败: {e}，{wait_time} 秒后重试（第 {attempt + 1}/{max_retries - 1} 次重试）...", file=sys.stderr)
                time.sleep(wait_time)
            else:
                print(f"错误：API 调用失败: {e}", file=sys.stderr)
                return None

        except json.JSONDecodeError as e:
            print(f"错误：JSON 解析失败: {e}", file=sys.stderr)
            if "choices" in result and len(result["choices"]) > 0:
                raw_content = result["choices"][0]["message"]["content"]
                print(f"原始响应（前500字符）: {raw_content[:500]}", file=sys.stderr)
            return None

    return None


def load_persons() -> Dict[str, Dict]:
    """加载所有人物实体，构建名称索引"""
    persons_file = ENTITIES_DIR / "persons.jsonl"

    if not persons_file.exists():
        print(f"错误：人物实体文件不存在: {persons_file}", file=sys.stderr)
        sys.exit(1)

    persons = {}
    with open(persons_file, 'r', encoding='utf-8') as f:
        for line in f:
            entity = json.loads(line)
            name = entity['name']
            persons[name] = entity

            # 也索引别名
            for alias in entity.get('aliases', []):
                if alias not in persons:
                    persons[alias] = entity

    return persons


def load_article(article_id: str) -> Optional[Dict]:
    """加载文章元数据"""
    volume_id = article_id.rsplit('-article-', 1)[0]
    articles_file = ARTICLES_DIR / f"{volume_id}.articles.jsonl"

    if not articles_file.exists():
        print(f"错误：文章文件不存在: {articles_file}", file=sys.stderr)
        return None

    with open(articles_file, 'r', encoding='utf-8') as f:
        for line in f:
            article = json.loads(line)
            if article['article_id'] == article_id:
                return article

    print(f"错误：未找到文章: {article_id}", file=sys.stderr)
    return None


def load_article_content(article: Dict, max_length: int = 4000) -> str:
    """加载文章正文内容"""
    volume_id = article['volume_id']
    cleaned_file = CLEANED_DIR / f"{volume_id}.cleaned.md"

    if not cleaned_file.exists():
        print(f"错误：cleaned markdown 文件不存在: {cleaned_file}", file=sys.stderr)
        return ""

    if article.get('content_lines') is None:
        print(f"警告：文章 {article['article_id']} 没有 content_lines，跳过", file=sys.stderr)
        return ""

    with open(cleaned_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = article['content_lines']['start']
    end = article['content_lines']['end']

    content_lines = lines[start:end+1]
    content = ''.join(content_lines)

    if len(content) > max_length:
        content = content[:max_length] + "\n\n[注：文章过长，仅显示前 4000 字]"

    return content


def find_persons_in_article(article_id: str, persons_index: Dict[str, Dict]) -> List[Dict]:
    """找出文章中出现的所有人物"""
    article_persons = []

    for name, entity in persons_index.items():
        # 检查该人物是否在这篇文章中出现
        for mention in entity.get('mentions', []):
            # 从 source_article 或 merged_articles 判断
            if 'source_article' in entity and entity['source_article'] == article_id:
                if entity not in article_persons:
                    article_persons.append(entity)
                break
            elif 'merged_articles' in entity and article_id in entity['merged_articles']:
                if entity not in article_persons:
                    article_persons.append(entity)
                break

    return article_persons


def build_relation_prompt(article: Dict, content: str, persons: List[Dict]) -> tuple[str, str]:
    """构建关系抽取 prompt"""
    system_message = """你是一个专业的历史文本关系抽取助手。你的任务是从毛泽东选集的文章中准确识别人物之间的关系。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的关系，不要推测
3. 关系必须在给定的人物列表中
4. 对于不确定的关系，设置 confidence < 0.8
5. 必须包含支持证据（上下文片段）"""

    # 构建人物列表
    person_names = [p['name'] for p in persons]
    person_list_str = '、'.join(person_names[:20])  # 最多显示前20个
    if len(person_names) > 20:
        person_list_str += f"等（共 {len(person_names)} 人）"

    user_prompt = f"""请从以下文章中抽取人物之间的关系。

## 文章中的人物

{person_list_str}

## 关系类型

支持以下关系类型：
- colleague_of: 同事、战友关系
- leader_of: 领导关系
- member_of: 成员关系（人物 -> 组织，组织名称可以从文本推断）
- opposed_to: 对立关系
- cooperated_with: 合作关系
- influenced_by: 受...影响

## 输出格式

返回 JSON 对象，包含 relations 数组：

{{
  "relations": [
    {{
      "from_person": "人物A名称",
      "to_person": "人物B名称或组织名称",
      "relation_type": "关系类型",
      "confidence": 0.0-1.0,
      "context": "支持该关系的上下文片段"
    }}
  ]
}}

## 待抽取文章

**卷册**: {article['volume_id']}
**文章**: {article['title']}
**日期**: {article.get('date_iso', 'N/A')}

**正文内容**:
{content}

请严格按照上述格式返回 JSON 结果。只返回文章中明确提到的关系。"""

    return system_message, user_prompt


def generate_relation_id(from_name: str, to_name: str, relation_type: str) -> str:
    """生成关系 ID"""
    content = f"{from_name}-{relation_type}-{to_name}"
    hash_obj = hashlib.md5(content.encode('utf-8'))
    return f"rel-{hash_obj.hexdigest()[:8]}"


def extract_relations(article: Dict, content: str, persons: List[Dict], persons_index: Dict[str, Dict]) -> List[Dict]:
    """抽取文章中的人物关系"""
    if len(persons) < 2:
        print(f"  文章中人物少于2个，跳过关系抽取")
        return []

    system_message, user_prompt = build_relation_prompt(article, content, persons)

    print(f"正在抽取关系: {article['article_id']} - {article['title']} ({len(persons)} 个人物)")

    result = call_deepseek_api(system_message, user_prompt)

    if result and 'relations' in result:
        relations = result['relations']

        # 补充元数据
        processed_relations = []
        for rel in relations:
            from_name = rel.get('from_person')
            to_name = rel.get('to_person')
            relation_type = rel.get('relation_type')

            if not from_name or not to_name or not relation_type:
                continue

            # 查找实体
            from_entity = persons_index.get(from_name)
            if not from_entity:
                continue

            # to_entity 可能是人物，也可能是组织（从文本推断）
            to_entity = persons_index.get(to_name)

            processed_rel = {
                'relation_id': generate_relation_id(from_name, to_name, relation_type),
                'from_entity_name': from_name,
                'from_entity_type': 'person',
                'to_entity_name': to_name,
                'to_entity_type': 'person' if to_entity else 'organization',
                'relation_type': relation_type,
                'confidence': rel.get('confidence', 0.9),
                'evidence': [{
                    'volume_id': article['volume_id'],
                    'article_id': article['article_id'],
                    'article_title': article['title'],
                    'context': rel.get('context', '')
                }],
                'extracted_at': datetime.now().isoformat()
            }

            processed_relations.append(processed_rel)

        print(f"  抽取到 {len(processed_relations)} 个关系")
        return processed_relations
    else:
        print(f"  抽取失败", file=sys.stderr)
        return []


def save_relations(relations: List[Dict]):
    """保存关系到 JSONL 文件"""
    RELATIONS_DIR.mkdir(parents=True, exist_ok=True)

    output_file = RELATIONS_DIR / "relations.jsonl"

    with open(output_file, 'a', encoding='utf-8') as f:
        for relation in relations:
            f.write(json.dumps(relation, ensure_ascii=False) + '\n')


def extract_article_relations(article_id: str, persons_index: Dict[str, Dict]):
    """抽取单篇文章的关系"""
    article = load_article(article_id)
    if not article:
        return

    content = load_article_content(article)
    if not content:
        return

    # 找出文章中的人物
    persons = find_persons_in_article(article_id, persons_index)

    # 抽取关系
    relations = extract_relations(article, content, persons, persons_index)
    if relations:
        save_relations(relations)

    # 等待一下，避免 API 限流
    time.sleep(1)


def extract_volume_relations(volume_id: str, persons_index: Dict[str, Dict], limit: Optional[int] = None):
    """抽取单卷的关系"""
    articles_file = ARTICLES_DIR / f"{volume_id}.articles.jsonl"

    if not articles_file.exists():
        print(f"错误：文章文件不存在: {articles_file}", file=sys.stderr)
        return

    articles = []
    with open(articles_file, 'r', encoding='utf-8') as f:
        for line in f:
            articles.append(json.loads(line))

    if limit:
        articles = articles[:limit]

    print(f"开始抽取 {volume_id} 的关系，共 {len(articles)} 篇文章")

    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] ", end='')
        extract_article_relations(article['article_id'], persons_index)


def extract_all_relations(persons_index: Dict[str, Dict]):
    """抽取全部卷册的关系"""
    volume_ids = [
        'mao-volume-01', 'mao-volume-02', 'mao-volume-03', 'mao-volume-04',
        'mao-volume-05', 'mao-volume-06', 'mao-volume-07'
    ]

    print(f"开始抽取全部卷册的关系...")

    for volume_id in volume_ids:
        extract_volume_relations(volume_id, persons_index)
        print(f"{volume_id} 完成\n")


def main():
    parser = argparse.ArgumentParser(description='关系抽取脚本')
    parser.add_argument('--article', help='抽取单篇文章，指定 article_id')
    parser.add_argument('--volume', help='抽取单卷，指定 volume_id')
    parser.add_argument('--limit', type=int, help='限制抽取文章数量（配合 --volume 使用）')
    parser.add_argument('--all', action='store_true', help='抽取全部卷册')

    args = parser.parse_args()

    # 加载人物实体
    print("正在加载人物实体...")
    persons_index = load_persons()
    print(f"已加载 {len(persons_index)} 个人物实体（含别名）\n")

    if args.article:
        extract_article_relations(args.article, persons_index)
    elif args.volume:
        extract_volume_relations(args.volume, persons_index, args.limit)
    elif args.all:
        extract_all_relations(persons_index)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
