#!/usr/bin/env python3
"""
实体抽取脚本

使用 DeepSeek API 从文章中抽取实体。

用法：
    python scripts/extract_entities.py --article mao-volume-01-article-001
    python scripts/extract_entities.py --volume mao-volume-01 --limit 5
    python scripts/extract_entities.py --all
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
import requests


# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = PROJECT_ROOT / "data" / "index" / "articles"
ENTITIES_DIR = PROJECT_ROOT / "data" / "index" / "entities"
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
                timeout=120  # 增加到 120 秒
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


def load_article_content(article: Dict, max_length: int = 5000) -> str:
    """加载文章正文内容，限制长度避免超时"""
    volume_id = article['volume_id']
    cleaned_file = CLEANED_DIR / f"{volume_id}.cleaned.md"

    if not cleaned_file.exists():
        print(f"错误：cleaned markdown 文件不存在: {cleaned_file}", file=sys.stderr)
        return ""

    # 检查 content_lines 是否存在
    if article.get('content_lines') is None:
        print(f"警告：文章 {article['article_id']} 没有 content_lines，跳过", file=sys.stderr)
        return ""

    with open(cleaned_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = article['content_lines']['start']
    end = article['content_lines']['end']

    content_lines = lines[start:end+1]
    content = ''.join(content_lines)

    # 如果内容过长，只取前 max_length 字符
    if len(content) > max_length:
        content = content[:max_length] + "\n\n[注：文章过长，仅显示前 5000 字]"

    return content


def build_person_prompt(article: Dict, content: str) -> tuple[str, str]:
    """构建人物抽取 prompt"""
    system_message = """你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取人物实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的人物，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含上下文片段（前后各 20 字符）
5. 必须包含文本位置信息（在文章中第几次出现）"""

    # 限制 prompt 中的内容长度，避免超时
    max_content_length = 4000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "\n\n[注：文章较长，仅显示部分内容]"

    user_prompt = f"""请从以下文章中抽取所有人物实体。

## 实体定义

人物实体包括：
- 历史人物：政治家、军事家、思想家、革命家等
- 作者和编者
- 文章中提到的具体个人
- 不包括：泛指的群体（如"工人"、"农民"）
- 不包括：神话人物、传说人物、虚构人物（如"赵公元帅"、"关公"等）

## 输出格式

返回 JSON 对象，包含 persons 数组：

{{
  "persons": [
    {{
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {{
        "roles": ["角色1", "角色2"],
        "affiliations": ["所属组织1"]
      }},
      "mentions": [
        {{
          "context": "...上下文片段...",
          "mention_index": 1
        }}
      ],
      "confidence": 0.0-1.0
    }}
  ]
}}

## 待抽取文章

**卷册**: {article['volume_id']}
**文章**: {article['title']}
**日期**: {article.get('date_iso', 'N/A')}

**正文内容**:
{content}

请严格按照上述格式返回 JSON 结果。只返回真实的历史人物，不要包含神话或虚构人物。"""

    return system_message, user_prompt


def build_place_prompt(article: Dict, content: str) -> tuple[str, str]:
    """构建地点抽取 prompt"""
    system_message = """你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取地点实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的地点，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含上下文片段（前后各 20 字符）
5. 必须包含文本位置信息（在文章中第几次出现）"""

    max_content_length = 4000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "\n\n[注：文章较长，仅显示部分内容]"

    user_prompt = f"""请从以下文章中抽取所有地点实体。

## 实体定义

地点实体包括：
- 国家、省份、城市、县、乡镇、村庄
- 山川河流、地理区域
- 具体地标（如"井冈山"、"延安"）
- 历史地名和现代地名
- 不包括：泛指的方位（如"东方"、"西方"）

## 输出格式

返回 JSON 对象，包含 places 数组：

{{
  "places": [
    {{
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {{
        "place_type": "地点类型（国家/省份/城市/山川等）",
        "modern_name": "现代名称（如果与历史名称不同）"
      }},
      "mentions": [
        {{
          "context": "...上下文片段...",
          "mention_index": 1
        }}
      ],
      "confidence": 0.0-1.0
    }}
  ]
}}

## 待抽取文章

**卷册**: {article['volume_id']}
**文章**: {article['title']}
**日期**: {article.get('date_iso', 'N/A')}

**正文内容**:
{content}

请严格按照上述格式返回 JSON 结果。"""

    return system_message, user_prompt


def build_organization_prompt(article: Dict, content: str) -> tuple[str, str]:
    """构建组织抽取 prompt"""
    system_message = """你是一个专业的历史文本实体抽取助手。你的任务是从毛泽东选集的文章中准确识别和抽取组织实体。

要求：
1. 必须返回有效的 JSON 格式
2. 只抽取明确提到的组织，不要推测
3. 对于不确定的实体，设置 confidence < 0.8
4. 必须包含上下文片段（前后各 20 字符）
5. 必须包含文本位置信息（在文章中第几次出现）"""

    max_content_length = 4000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "\n\n[注：文章较长，仅显示部分内容]"

    user_prompt = f"""请从以下文章中抽取所有组织实体。

## 实体定义

组织实体包括：
- 政党：中国共产党、国民党等
- 政府机构：国民政府、苏维埃政府等
- 军事组织：红军、国民革命军等
- 社会团体：工会、农会、秘密会社等
- 国际组织：共产国际、国际联盟等
- 学校、报社、出版社
- 不包括：泛指的群体（如"地主阶级"、"工人阶级"）

## 输出格式

返回 JSON 对象，包含 organizations 数组：

{{
  "organizations": [
    {{
      "name": "标准名称",
      "aliases": ["别名1", "别名2"],
      "attributes": {{
        "organization_type": "组织类型",
        "founded_date": "成立日期（如有）"
      }},
      "mentions": [
        {{
          "context": "...上下文片段...",
          "mention_index": 1
        }}
      ],
      "confidence": 0.0-1.0
    }}
  ]
}}

## 待抽取文章

**卷册**: {article['volume_id']}
**文章**: {article['title']}
**日期**: {article.get('date_iso', 'N/A')}

**正文内容**:
{content}

请严格按照上述格式返回 JSON 结果。"""

    return system_message, user_prompt


def extract_persons(article: Dict, content: str) -> List[Dict]:
    """抽取人物实体"""
    system_message, user_prompt = build_person_prompt(article, content)

    print(f"正在抽取人物实体: {article['article_id']} - {article['title']}")

    result = call_deepseek_api(system_message, user_prompt)

    if result and 'persons' in result:
        persons = result['persons']

        # 补充元数据
        for person in persons:
            person['entity_type'] = 'person'
            person['source_article'] = article['article_id']
            person['source_volume'] = article['volume_id']
            person['article_title'] = article['title']
            person['article_date'] = article.get('date_iso')

        print(f"  抽取到 {len(persons)} 个人物实体")
        return persons
    else:
        print(f"  抽取失败", file=sys.stderr)
        return []


def extract_places(article: Dict, content: str) -> List[Dict]:
    """抽取地点实体"""
    system_message, user_prompt = build_place_prompt(article, content)

    print(f"正在抽取地点实体: {article['article_id']} - {article['title']}")

    result = call_deepseek_api(system_message, user_prompt)

    if result and 'places' in result:
        places = result['places']

        # 补充元数据
        for place in places:
            place['entity_type'] = 'place'
            place['source_article'] = article['article_id']
            place['source_volume'] = article['volume_id']
            place['article_title'] = article['title']
            place['article_date'] = article.get('date_iso')

        print(f"  抽取到 {len(places)} 个地点实体")
        return places
    else:
        print(f"  抽取失败", file=sys.stderr)
        return []


def extract_organizations(article: Dict, content: str) -> List[Dict]:
    """抽取组织实体"""
    system_message, user_prompt = build_organization_prompt(article, content)

    print(f"正在抽取组织实体: {article['article_id']} - {article['title']}")

    result = call_deepseek_api(system_message, user_prompt)

    if result and 'organizations' in result:
        organizations = result['organizations']

        # 补充元数据
        for org in organizations:
            org['entity_type'] = 'organization'
            org['source_article'] = article['article_id']
            org['source_volume'] = article['volume_id']
            org['article_title'] = article['title']
            org['article_date'] = article.get('date_iso')

        print(f"  抽取到 {len(organizations)} 个组织实体")
        return organizations
    else:
        print(f"  抽取失败", file=sys.stderr)
        return []


def save_entities(entities: List[Dict], entity_type: str):
    """保存实体到 JSONL 文件"""
    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)

    output_file = ENTITIES_DIR / f"{entity_type}s.jsonl"

    with open(output_file, 'a', encoding='utf-8') as f:
        for entity in entities:
            f.write(json.dumps(entity, ensure_ascii=False) + '\n')


def extract_article(article_id: str, entity_type: str = 'person'):
    """抽取单篇文章的实体"""
    article = load_article(article_id)
    if not article:
        return

    content = load_article_content(article)
    if not content:
        return

    # 根据实体类型选择抽取函数
    if entity_type == 'person':
        entities = extract_persons(article, content)
    elif entity_type == 'place':
        entities = extract_places(article, content)
    elif entity_type == 'organization':
        entities = extract_organizations(article, content)
    else:
        print(f"错误：不支持的实体类型: {entity_type}", file=sys.stderr)
        return

    if entities:
        save_entities(entities, entity_type)

    # 等待一下，避免 API 限流
    time.sleep(1)


def extract_volume(volume_id: str, entity_type: str = 'person', limit: Optional[int] = None):
    """抽取单卷的实体"""
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

    print(f"开始抽取 {volume_id} 的 {entity_type} 实体，共 {len(articles)} 篇文章")

    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] ", end='')
        extract_article(article['article_id'], entity_type)


def extract_all(entity_type: str = 'person'):
    """抽取全部卷册的实体"""
    volume_ids = [
        'mao-volume-01', 'mao-volume-02', 'mao-volume-03', 'mao-volume-04',
        'mao-volume-05', 'mao-volume-06', 'mao-volume-07'
    ]

    print(f"开始抽取全部卷册的 {entity_type} 实体...")

    for volume_id in volume_ids:
        extract_volume(volume_id, entity_type)
        print(f"{volume_id} 完成\n")


def main():
    parser = argparse.ArgumentParser(description='实体抽取脚本')
    parser.add_argument('--article', help='抽取单篇文章，指定 article_id')
    parser.add_argument('--volume', help='抽取单卷，指定 volume_id')
    parser.add_argument('--limit', type=int, help='限制抽取文章数量（配合 --volume 使用）')
    parser.add_argument('--all', action='store_true', help='抽取全部卷册')
    parser.add_argument('--entity-type', type=str, default='person',
                        choices=['person', 'place', 'organization'],
                        help='实体类型 (默认: person)')

    args = parser.parse_args()

    if args.article:
        extract_article(args.article, args.entity_type)
    elif args.volume:
        extract_volume(args.volume, args.entity_type, args.limit)
    elif args.all:
        extract_all(args.entity_type)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
