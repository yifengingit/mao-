#!/usr/bin/env python3
"""
文章摘要生成脚本

从清洗后的 Markdown 中提取每篇文章的前几段正文，
生成 article_excerpts.json 供前端展示。

用法：
    python scripts/build_article_excerpts.py
"""

import json
from pathlib import Path

PROJECT_ROOT  = Path(__file__).parent.parent
ARTICLES_DIR  = PROJECT_ROOT / "data" / "index" / "articles"
CLEAN_DIR     = PROJECT_ROOT / "data" / "clean" / "volumes"
GRAPH_DIR     = PROJECT_ROOT / "data" / "index" / "graph"

EXCERPT_CHARS = 300   # 正文截取字符数


def load_jsonl(path: Path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def extract_excerpt(md_lines: list, content_lines: dict, max_chars: int = EXCERPT_CHARS) -> str:
    """从 cleaned markdown 中按行号截取正文片段。"""
    start = content_lines.get("start", 1) - 1   # 0-indexed
    end   = content_lines.get("end",   start + 20)
    # 最多取 20 行，然后截断到 max_chars 字符
    chunk_lines = md_lines[start : min(start + 20, end)]
    text = "".join(chunk_lines).strip()
    # 去掉多余空行
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars]


def main():
    excerpts: dict = {}

    volume_ids = [f"mao-volume-0{i}" for i in range(1, 8)]

    for vol_id in volume_ids:
        articles_file = ARTICLES_DIR / f"{vol_id}.articles.jsonl"
        clean_file    = CLEAN_DIR    / f"{vol_id}.cleaned.md"

        if not articles_file.exists():
            print(f"跳过 {vol_id}: articles.jsonl 不存在")
            continue
        if not clean_file.exists():
            print(f"跳过 {vol_id}: cleaned.md 不存在")
            continue

        articles  = load_jsonl(articles_file)
        md_lines  = clean_file.read_text(encoding="utf-8").splitlines(keepends=True)

        print(f"处理 {vol_id}: {len(articles)} 篇文章, {len(md_lines)} 行 Markdown")

        for art in articles:
            article_id    = art["article_id"]
            title         = art.get("title", "")
            date_iso      = art.get("date_iso", "")
            content_lines = art.get("content_lines", {})

            excerpt = extract_excerpt(md_lines, content_lines or {})

            excerpts[article_id] = {
                "article_id": article_id,
                "volume_id":  vol_id,
                "title":      title,
                "date_iso":   date_iso,
                "excerpt":    excerpt,
            }

    # 写出
    out_path = GRAPH_DIR / "article_excerpts.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(excerpts, f, ensure_ascii=False, indent=2)

    print(f"\n完成: {len(excerpts)} 条摘要 -> {out_path}")


if __name__ == "__main__":
    main()
