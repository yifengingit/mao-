#!/usr/bin/env python3
"""
重新处理失败文章的脚本

用法：
    python scripts/retry_failed_articles.py
    python scripts/retry_failed_articles.py --no-dedup   # 跑完后不自动去重
"""

import argparse
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path
from extract_entities import extract_article

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ENTITIES_DIR = PROJECT_ROOT / "data" / "index" / "entities"
SCRIPTS_DIR = Path(__file__).parent


def load_failed_articles():
    """加载失败文章列表"""
    failed_file = ENTITIES_DIR / "failed_articles.txt"
    if not failed_file.exists():
        print(f"错误：失败文章列表不存在: {failed_file}", file=sys.stderr)
        sys.exit(1)
    articles = []
    with open(failed_file, 'r', encoding='utf-8') as f:
        for line in f:
            article_id = line.strip()
            if article_id:
                articles.append(article_id)
    return articles


def update_failed_articles(still_failed: list):
    """将仍然失败的文章写回 failed_articles.txt"""
    failed_file = ENTITIES_DIR / "failed_articles.txt"
    with open(failed_file, 'w', encoding='utf-8') as f:
        for article_id in still_failed:
            f.write(article_id + '\n')


def fmt_duration(seconds: float) -> str:
    """将秒数格式化为 m:ss"""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    m, s = divmod(total_seconds, 60)
    return f"{m}:{s:02d}"


def print_progress(i: int, total: int, article_id: str,
                   success: int, fail: int,
                   elapsed: float, avg_per_article: float):
    """打印一行进度信息"""
    remaining = total - i
    eta = avg_per_article * remaining if avg_per_article > 0 else 0
    speed = 60 / avg_per_article if avg_per_article > 0 else 0

    print(
        f"[{i}/{total}] {article_id}"
        f"  |  used:{fmt_duration(elapsed)}"
        f"  |  ETA:{fmt_duration(eta)}"
        f"  |  {speed:.1f}/min"
        f"  |  ok={success} fail={fail}"
    )


def run_deduplication():
    """重新运行人物实体去重"""
    print("\n── 开始重新去重人物实体 ──")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "deduplicate_entities.py"), "--entity-type", "person"],
        cwd=str(SCRIPTS_DIR),
        capture_output=False
    )
    if result.returncode != 0:
        print("警告：去重脚本返回非零退出码", file=sys.stderr)
    else:
        print("去重完成。")


def main():
    parser = argparse.ArgumentParser(description='重新处理失败文章')
    parser.add_argument('--no-dedup', action='store_true', help='完成后不自动重跑去重')
    args = parser.parse_args()

    failed_articles = load_failed_articles()
    total = len(failed_articles)
    print(f"共 {total} 篇失败文章，开始重跑...\n")

    success_count = 0
    fail_count = 0
    still_failed = []

    start_time = time.time()
    article_times = []  # 记录每篇文章的耗时，用于计算滚动平均

    for i, article_id in enumerate(failed_articles, 1):
        article_start = time.time()

        try:
            extract_article(article_id, entity_type='person')
            success_count += 1
        except Exception as e:
            print(f"  处理失败: {e}", file=sys.stderr)
            fail_count += 1
            still_failed.append(article_id)

        article_elapsed = time.time() - article_start
        article_times.append(article_elapsed)

        # 用最近 10 篇的滚动平均计算 ETA，更贴近当前 API 响应速度
        recent = article_times[-10:]
        avg = sum(recent) / len(recent)

        total_elapsed = time.time() - start_time
        print_progress(i, total, article_id, success_count, fail_count, total_elapsed, avg)

    total_elapsed = time.time() - start_time

    print(f"\n{'─' * 50}")
    print(f"重跑完成！总耗时: {fmt_duration(total_elapsed)}")
    print(f"  成功: {success_count} 篇")
    print(f"  失败: {fail_count} 篇")
    print(f"  成功率: {success_count / total * 100:.1f}%")

    # 更新 failed_articles.txt，只保留仍然失败的
    update_failed_articles(still_failed)
    if still_failed:
        print(f"\n仍有 {len(still_failed)} 篇文章失败，已写回 failed_articles.txt")
    else:
        print("\n所有失败文章已全部处理完毕，failed_articles.txt 已清空")

    # 自动重跑去重
    if not args.no_dedup:
        run_deduplication()


if __name__ == '__main__':
    main()
