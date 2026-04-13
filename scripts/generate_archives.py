#!/usr/bin/env python3
"""
档案生成脚本

将人物、地点实体与关系数据聚合为结构化档案 JSON。
每个实体一个档案文件，另生成全局索引。

用法：
    python scripts/generate_archives.py --type person
    python scripts/generate_archives.py --type place
    python scripts/generate_archives.py --all
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
ENTITIES_DIR  = PROJECT_ROOT / "data" / "index" / "entities"
RELATIONS_DIR = PROJECT_ROOT / "data" / "index" / "relations"
ARCHIVES_DIR  = PROJECT_ROOT / "data" / "index" / "archives"


# ─────────────────────────── 工具函数 ────────────────────────────

def slugify(name: str) -> str:
    """生成 URL 安全的 slug（保留中文，去掉非法字符）"""
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        print(f"警告：文件不存在: {path}", file=sys.stderr)
        return []
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_json(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────── 关系索引构建 ────────────────────────────

def build_relation_index(relations: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按实体名称建立关系索引。
    index[name] = [ relation, relation, ... ]
    每条关系包含对方名称、关系类型、证据等。
    """
    index = defaultdict(list)
    for rel in relations:
        src = rel.get("from_entity_name", "")
        dst = rel.get("to_entity_name", "")
        if src:
            index[src].append(rel)
        if dst and dst != src:
            # 反向也建索引，方便双向查询
            index[dst].append(rel)
    return index


# ─────────────────────── 人物档案生成 ─────────────────────────────

def build_person_archive(person: Dict, relation_index: Dict, archive_id: str) -> Dict:
    name = person["name"]
    mentions = person.get("mentions", [])
    attributes = person.get("attributes", {})

    # ── 关联实体（从关系表中聚合）──
    related_persons = []
    related_orgs = []
    seen_related = set()

    for rel in relation_index.get(name, []):
        src = rel.get("from_entity_name", "")
        dst = rel.get("to_entity_name", "")
        dst_type = rel.get("to_entity_type", "")
        src_type = rel.get("from_entity_type", "")
        rtype = rel.get("relation_type", "")
        evidence = rel.get("evidence", [])
        source_articles = [e.get("article_id") for e in evidence if e.get("article_id")]

        # 确定对方是谁
        if src == name:
            other_name = dst
            other_type = dst_type
        else:
            other_name = src
            other_type = src_type

        if not other_name or other_name in seen_related:
            continue
        seen_related.add(other_name)

        entry = {
            "name": other_name,
            "relation_type": rtype,
            "source_articles": source_articles,
            "confidence": rel.get("confidence", 1.0),
        }
        if other_type == "person":
            related_persons.append(entry)
        elif other_type == "organization":
            related_orgs.append(entry)

    # ── 来源文献（按卷分组）──
    article_map: Dict[str, Dict] = {}  # article_id -> {title, volume_id, mention_count}
    for m in mentions:
        # mention 里没有直接的 article_id，但 person 记录本身有 source_article
        pass

    # person 记录里有 merged_articles（去重后）或 source_article（单条）
    article_ids = person.get("merged_articles") or []
    if not article_ids and person.get("source_article"):
        article_ids = [person["source_article"]]

    # 构建 references（按 volume 分组）
    vol_map: Dict[str, List] = defaultdict(list)
    for art_id in article_ids:
        vol_id = art_id.rsplit("-article-", 1)[0] if "-article-" in art_id else "unknown"
        mention_count = sum(
            1 for m in mentions
            # mentions 没有 article_id 字段，用实体级别的 source_article 作为近似
        )
        vol_map[vol_id].append({
            "article_id": art_id,
            "mention_count": len(mentions),  # 近似值，去重后 mentions 是全量合并
        })

    references = [
        {"volume_id": vol_id, "articles": arts}
        for vol_id, arts in sorted(vol_map.items())
    ]

    # ── 统计 ──
    source_volumes = person.get("source_volumes") or (
        [person["source_volume"]] if person.get("source_volume") else []
    )
    stats = {
        "total_mentions": len(mentions),
        "total_articles": len(article_ids),
        "total_volumes": len(source_volumes),
        "related_persons": len(related_persons),
        "related_organizations": len(related_orgs),
    }

    ts = now_iso()
    return {
        "archive_id": archive_id,
        "archive_type": "person_archive",
        "name": name,
        "aliases": person.get("aliases", []),
        "summary": "",  # 预留，后续 LLM 生成
        "attributes": {
            "roles": attributes.get("roles", []),
            "affiliations": attributes.get("affiliations", []),
        },
        "related_entities": {
            "persons": related_persons,
            "organizations": related_orgs,
        },
        "references": references,
        "statistics": stats,
        "confidence": person.get("confidence", 1.0),
        "created_at": ts,
        "updated_at": ts,
    }


def generate_person_archives(relations: List[Dict]) -> List[Dict]:
    """生成全部人物档案，返回索引条目列表"""
    persons = load_jsonl(ENTITIES_DIR / "persons.deduplicated.jsonl")
    if not persons:
        print("错误：persons.deduplicated.jsonl 不存在或为空", file=sys.stderr)
        return []

    relation_index = build_relation_index(relations)
    out_dir = ARCHIVES_DIR / "person_archives"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []
    total = len(persons)

    print(f"开始生成人物档案，共 {total} 条...")
    for i, person in enumerate(persons, 1):
        name = person["name"]
        archive_id = f"archive-person-{i:04d}"
        slug = slugify(name)
        filename = f"{archive_id}_{slug}.json"

        archive = build_person_archive(person, relation_index, archive_id)
        write_json(out_dir / filename, archive)

        index_entries.append({
            "archive_id": archive_id,
            "archive_type": "person_archive",
            "name": name,
            "aliases": person.get("aliases", []),
            "file": f"person_archives/{filename}",
            "statistics": archive["statistics"],
        })

        if i % 50 == 0 or i == total:
            print(f"  [{i}/{total}] 已完成")

    print(f"人物档案生成完毕，共 {total} 个文件 -> {out_dir}")
    return index_entries


# ─────────────────────── 地点档案生成 ─────────────────────────────

def build_place_archive(place: Dict, archive_id: str) -> Dict:
    name = place["name"]
    mentions = place.get("mentions", [])
    attributes = place.get("attributes", {})

    article_ids = place.get("merged_articles") or []
    if not article_ids and place.get("source_article"):
        article_ids = [place["source_article"]]

    vol_map: Dict[str, List] = defaultdict(list)
    for art_id in article_ids:
        vol_id = art_id.rsplit("-article-", 1)[0] if "-article-" in art_id else "unknown"
        vol_map[vol_id].append({"article_id": art_id})

    references = [
        {"volume_id": vol_id, "articles": arts}
        for vol_id, arts in sorted(vol_map.items())
    ]

    source_volumes = place.get("source_volumes") or (
        [place["source_volume"]] if place.get("source_volume") else []
    )
    stats = {
        "total_mentions": len(mentions),
        "total_articles": len(article_ids),
        "total_volumes": len(source_volumes),
    }

    ts = now_iso()
    return {
        "archive_id": archive_id,
        "archive_type": "place_archive",
        "name": name,
        "aliases": place.get("aliases", []),
        "summary": "",  # 预留，后续 LLM 生成
        "attributes": {
            "place_type": attributes.get("place_type", ""),
            "modern_name": attributes.get("modern_name", ""),
        },
        "references": references,
        "statistics": stats,
        "confidence": place.get("confidence", 1.0),
        "created_at": ts,
        "updated_at": ts,
    }


def generate_place_archives() -> List[Dict]:
    """生成全部地点档案，返回索引条目列表"""
    places = load_jsonl(ENTITIES_DIR / "places.deduplicated.jsonl")
    if not places:
        print("错误：places.deduplicated.jsonl 不存在或为空", file=sys.stderr)
        return []

    out_dir = ARCHIVES_DIR / "place_archives"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []
    total = len(places)

    print(f"开始生成地点档案，共 {total} 条...")
    for i, place in enumerate(places, 1):
        name = place["name"]
        archive_id = f"archive-place-{i:04d}"
        slug = slugify(name)
        filename = f"{archive_id}_{slug}.json"

        archive = build_place_archive(place, archive_id)
        write_json(out_dir / filename, archive)

        index_entries.append({
            "archive_id": archive_id,
            "archive_type": "place_archive",
            "name": name,
            "aliases": place.get("aliases", []),
            "file": f"place_archives/{filename}",
            "statistics": archive["statistics"],
        })

        if i % 50 == 0 or i == total:
            print(f"  [{i}/{total}] 已完成")

    print(f"地点档案生成完毕，共 {total} 个文件 -> {out_dir}")
    return index_entries


# ──────────────────────── 全局索引生成 ────────────────────────────

def write_global_index(all_entries: List[Dict]):
    index_path = ARCHIVES_DIR / "index.json"
    index = {
        "generated_at": now_iso(),
        "total": len(all_entries),
        "by_type": {},
        "entries": all_entries,
    }
    for entry in all_entries:
        t = entry["archive_type"]
        index["by_type"][t] = index["by_type"].get(t, 0) + 1

    write_json(index_path, index)
    print(f"\n全局索引已写入: {index_path}")
    print(f"  总档案数: {index['total']}")
    for t, cnt in index["by_type"].items():
        print(f"  {t}: {cnt}")


# ────────────────────────────── main ──────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="档案生成脚本")
    parser.add_argument("--type", choices=["person", "place"], help="只生成指定类型")
    parser.add_argument("--all", action="store_true", help="生成所有类型（person + place）")
    args = parser.parse_args()

    if not args.type and not args.all:
        parser.print_help()
        sys.exit(1)

    relations = load_jsonl(RELATIONS_DIR / "relations.deduplicated.jsonl")
    print(f"加载关系数据: {len(relations)} 条\n")

    all_index_entries = []

    if args.all or args.type == "person":
        entries = generate_person_archives(relations)
        all_index_entries.extend(entries)
        print()

    if args.all or args.type == "place":
        entries = generate_place_archives()
        all_index_entries.extend(entries)
        print()

    write_global_index(all_index_entries)


if __name__ == "__main__":
    main()
