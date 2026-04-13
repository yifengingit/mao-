#!/usr/bin/env python3
"""
文章切分脚本

从 cleaned markdown 文件中识别文章边界，将整卷文本切分为独立的文章单元。

用法：
    python scripts/segment_articles.py mao-volume-01
    python scripts/segment_articles.py --all
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# 中文数字映射
CHINESE_DIGITS = {
    '○': 0, '〇': 0, '零': 0,
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
}

# 日期正则表达式
DATE_PATTERN = re.compile(
    r'[（(]'  # 左括号（全角或半角）
    r'一九[○〇零一二三四五六七八九]{2}年'  # 年份
    r'(?:'  # 可选的月日部分
        r'(?:[一二三四五六七八九十]+月)?'  # 月份
        r'(?:[一二三四五六七八九十]+日)?'  # 日期
        r'|春|夏|秋|冬|至一九[○〇零一二三四五六七八九]{2}年[一二三四五六七八九十]+月'  # 或季节/日期范围
    r')?'
    r'[）)]'  # 右括号
)


def chinese_to_arabic(cn_num: str) -> int:
    """将中文数字转换为阿拉伯数字"""
    if not cn_num:
        return 0

    # 处理十位数
    if '十' in cn_num:
        parts = cn_num.split('十')
        if len(parts) == 2:
            tens = CHINESE_DIGITS.get(parts[0], 1) if parts[0] else 1
            ones = CHINESE_DIGITS.get(parts[1], 0) if parts[1] else 0
            return tens * 10 + ones
        elif len(parts) == 1:
            # 只有"十"
            return 10

    # 处理个位数
    result = 0
    for char in cn_num:
        result = result * 10 + CHINESE_DIGITS.get(char, 0)
    return result


def parse_date(date_str: str) -> Optional[str]:
    """将中文日期转换为 ISO 格式"""
    # 提取年份
    year_match = re.search(r'一九([○〇零一二三四五六七八九]{2})年', date_str)
    if not year_match:
        return None

    year_cn = year_match.group(1)
    year = 1900 + chinese_to_arabic(year_cn)

    # 提取月份
    month_match = re.search(r'([一二三四五六七八九十]+)月', date_str)
    month = chinese_to_arabic(month_match.group(1)) if month_match else 1

    # 提取日期
    day_match = re.search(r'([一二三四五六七八九十]+)日', date_str)
    day = chinese_to_arabic(day_match.group(1)) if day_match else 1

    return f"{year:04d}-{month:02d}-{day:02d}"


def is_title_line(line: str, next_lines: List[str]) -> bool:
    """判断是否是文章标题行"""
    stripped = line.strip()

    if not stripped:
        return False

    # 排除页码行
    if stripped.isdigit():
        return False

    # 排除注释标记
    if '注　　释' in stripped or stripped == '注释':
        return False

    # 排除脚注
    if re.match(r'^〔\d+〕', stripped):
        return False

    # 排除题注
    if re.match(r'^[*＊]', stripped):
        return False

    # 检查后续行是否是日期行或空行后是日期行
    for i, next_line in enumerate(next_lines[:5]):
        next_stripped = next_line.strip()
        if not next_stripped:
            continue
        if DATE_PATTERN.search(next_stripped):
            return True
        # 如果遇到非空非日期行，停止检查
        if i > 0:
            break

    return False


def count_words(text: str) -> int:
    """统计字数（不含标点和空格）"""
    # 移除标点和空格
    text = re.sub(r'[，。、；：！？""''（）《》【】\s]+', '', text)
    return len(text)


def count_paragraphs(lines: List[str]) -> int:
    """统计段落数量"""
    count = 0
    in_paragraph = False

    for line in lines:
        if line.strip():
            if not in_paragraph:
                count += 1
                in_paragraph = True
        else:
            in_paragraph = False

    return count


def segment_articles(volume_id: str, lines: List[str]) -> List[Dict]:
    """切分文章"""
    articles = []
    current_article = None
    in_notes = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 检查是否是注释区域开始
        if '注　　释' in stripped or stripped == '注释':
            in_notes = True
            if current_article:
                current_article['content_end'] = i - 1
                current_article['notes_start'] = i
            continue

        # 检查是否是文章标题
        if is_title_line(line, lines[i+1:i+6]):
            # 保存上一篇文章
            if current_article:
                if in_notes:
                    current_article['notes_end'] = i - 1
                else:
                    current_article['content_end'] = i - 1

                # 计算统计信息
                content_lines = lines[current_article['content_start']:current_article['content_end']+1]
                current_article['word_count'] = count_words(''.join(content_lines))
                current_article['paragraph_count'] = count_paragraphs(content_lines)

                articles.append(current_article)

            # 开始新文章
            title = stripped.rstrip('*＊')
            current_article = {
                'title': title,
                'has_title_note': stripped.endswith('*') or stripped.endswith('＊'),
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
        if current_article and current_article['date'] is None:
            date_match = DATE_PATTERN.search(stripped)
            if date_match:
                current_article['date'] = date_match.group(0)
                current_article['date_line'] = i
                current_article['content_start'] = i + 1
                continue

        # 如果有标题但没有日期，且已经过了几行，设置 content_start
        if current_article and current_article['date'] is None and current_article['content_start'] is None:
            if i - current_article['title_line'] > 3 and stripped:
                current_article['content_start'] = i

    # 保存最后一篇文章
    if current_article:
        if in_notes:
            current_article['notes_end'] = len(lines) - 1
        else:
            current_article['content_end'] = len(lines) - 1

        # 计算统计信息
        if current_article['content_start'] is not None:
            content_lines = lines[current_article['content_start']:current_article['content_end']+1]
            current_article['word_count'] = count_words(''.join(content_lines))
            current_article['paragraph_count'] = count_paragraphs(content_lines)
        else:
            current_article['word_count'] = 0
            current_article['paragraph_count'] = 0

        articles.append(current_article)

    # 生成 article_id 并转换为输出格式
    output_articles = []
    for seq, article in enumerate(articles, start=1):
        article_id = f"{volume_id}-article-{seq:03d}"

        output_article = {
            'article_id': article_id,
            'volume_id': volume_id,
            'title': article['title'],
            'has_title_note': article['has_title_note'],
            'date_original': article['date'],
            'date_iso': parse_date(article['date']) if article['date'] else None,
            'title_line': article['title_line'],
            'date_line': article['date_line'],
            'content_lines': {
                'start': article['content_start'],
                'end': article['content_end']
            } if article['content_start'] is not None else None,
            'notes_lines': {
                'start': article['notes_start'],
                'end': article['notes_end']
            } if article['notes_start'] is not None else None,
            'word_count': article['word_count'],
            'paragraph_count': article['paragraph_count']
        }

        output_articles.append(output_article)

    return output_articles


def process_volume(volume_id: str, base_dir: Path) -> Tuple[int, str]:
    """处理单个卷册"""
    # 读取 cleaned markdown
    cleaned_file = base_dir / 'data' / 'clean' / 'volumes' / f'{volume_id}.cleaned.md'

    if not cleaned_file.exists():
        return 0, f"文件不存在: {cleaned_file}"

    # 尝试多种编码读取
    lines = None
    for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'cp936']:
        try:
            with open(cleaned_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue

    if lines is None:
        return 0, f"无法读取文件: {cleaned_file}"

    # 切分文章
    articles = segment_articles(volume_id, lines)

    # 创建输出目录
    output_dir = base_dir / 'data' / 'index' / 'articles'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 输出 JSONL
    output_file = output_dir / f'{volume_id}.articles.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

    return len(articles), f"成功切分 {len(articles)} 篇文章，输出到 {output_file}"


def main():
    parser = argparse.ArgumentParser(description='文章切分脚本')
    parser.add_argument('volume_id', nargs='?', help='卷册 ID（如 mao-volume-01）')
    parser.add_argument('--all', action='store_true', help='处理全部卷册')

    args = parser.parse_args()

    # 确定项目根目录
    base_dir = Path(__file__).parent.parent

    if args.all:
        # 处理全部卷册
        volume_ids = [f'mao-volume-{i:02d}' for i in range(1, 8)]
        total_articles = 0

        print("开始处理全部卷册...")
        for volume_id in volume_ids:
            count, message = process_volume(volume_id, base_dir)
            total_articles += count
            print(f"[{volume_id}] {message}")

        print(f"\n总计切分 {total_articles} 篇文章")

    elif args.volume_id:
        # 处理单个卷册
        count, message = process_volume(args.volume_id, base_dir)
        print(message)

        if count == 0:
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
