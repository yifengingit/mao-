#!/usr/bin/env python3
"""
知识图谱构建脚本

从实体和关系数据构建 NetworkX 图，导出为 D3.js 可消费的 JSON。

用法：
    python scripts/build_graph.py
"""

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx

PROJECT_ROOT  = Path(__file__).parent.parent
ENTITIES_DIR  = PROJECT_ROOT / "data" / "index" / "entities"
RELATIONS_DIR = PROJECT_ROOT / "data" / "index" / "relations"
ARTICLES_DIR  = PROJECT_ROOT / "data" / "index" / "articles"
GRAPH_DIR     = PROJECT_ROOT / "data" / "index" / "graph"


def load_article_date_map() -> dict:
    """返回 {article_id: date_iso} 的映射，用于给边/节点打时间戳。"""
    date_map = {}
    for i in range(1, 8):
        path = ARTICLES_DIR / f"mao-volume-0{i}.articles.jsonl"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    art = json.loads(line)
                    if art.get("date_iso"):
                        date_map[art["article_id"]] = art["date_iso"]
    return date_map


def load_jsonl(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def build_graph():
    G = nx.DiGraph()
    date_map = load_article_date_map()
    print(f"文章日期索引: {len(date_map)} 条")

    # ── 人物节点 ──────────────────────────────────────────────────
    persons = load_jsonl(ENTITIES_DIR / "persons.deduplicated.jsonl")
    for p in persons:
        merged = p.get("merged_articles") or []
        if not merged and p.get("source_article"):
            merged = [p["source_article"]]
        dates = sorted(d for art in merged if (d := date_map.get(art)))
        G.add_node(
            p["name"],
            node_type="person",
            aliases=p.get("aliases", []),
            roles=p.get("attributes", {}).get("roles", []),
            affiliations=p.get("attributes", {}).get("affiliations", []),
            mention_count=len(p.get("mentions", [])),
            confidence=p.get("confidence", 1.0),
            first_seen=dates[0] if dates else "",
            last_seen=dates[-1] if dates else "",
        )
    print(f"人物节点: {len(persons)}")

    # ── 地点节点 ──────────────────────────────────────────────────
    places = load_jsonl(ENTITIES_DIR / "places.deduplicated.jsonl")
    for pl in places:
        merged = pl.get("merged_articles") or []
        if not merged and pl.get("source_article"):
            merged = [pl["source_article"]]
        dates = sorted(d for art in merged if (d := date_map.get(art)))
        G.add_node(
            pl["name"],
            node_type="place",
            aliases=pl.get("aliases", []),
            place_type=pl.get("attributes", {}).get("place_type", ""),
            modern_name=pl.get("attributes", {}).get("modern_name", ""),
            mention_count=len(pl.get("mentions", [])),
            confidence=pl.get("confidence", 1.0),
            first_seen=dates[0] if dates else "",
            last_seen=dates[-1] if dates else "",
        )
    print(f"地点节点: {len(places)}")

    # ── 关系 → 顺带提取组织节点 ───────────────────────────────────
    relations = load_jsonl(RELATIONS_DIR / "relations.deduplicated.jsonl")

    org_names = set()
    for rel in relations:
        if rel.get("from_entity_type") == "organization":
            org_names.add(rel["from_entity_name"])
        if rel.get("to_entity_type") == "organization":
            org_names.add(rel["to_entity_name"])

    for name in org_names:
        if name not in G:
            G.add_node(name, node_type="organization", mention_count=0,
                       first_seen="", last_seen="")
    print(f"组织节点（从关系提取）: {len(org_names)}")

    # ── 边 ────────────────────────────────────────────────────────
    edge_count = 0
    # 同时收集 org 的 first_seen / last_seen
    org_date_ranges: dict = defaultdict(list)

    for rel in relations:
        src = rel["from_entity_name"]
        dst = rel["to_entity_name"]
        if not src or not dst:
            continue
        if src not in G:
            G.add_node(src, node_type=rel.get("from_entity_type", "unknown"),
                       mention_count=0, first_seen="", last_seen="")
        if dst not in G:
            G.add_node(dst, node_type=rel.get("to_entity_type", "unknown"),
                       mention_count=0, first_seen="", last_seen="")

        evidence = rel.get("evidence", [])
        source_articles = [e["article_id"] for e in evidence if e.get("article_id")]

        # 取证据中最早的文章日期作为该关系的时间戳
        edge_dates = sorted(d for art in source_articles if (d := date_map.get(art)))
        first_date = edge_dates[0] if edge_dates else ""

        # 证据文本列表（供前端展示）
        evidence_items = [
            {
                "article_id":    e.get("article_id", ""),
                "article_title": e.get("article_title", ""),
                "date_iso":      date_map.get(e.get("article_id", ""), ""),
                "context":       e.get("context", ""),
            }
            for e in evidence if e.get("article_id")
        ]

        G.add_edge(
            src, dst,
            relation_type=rel.get("relation_type", ""),
            confidence=rel.get("confidence", 1.0),
            source_articles=source_articles,
            relation_id=rel.get("relation_id", ""),
            first_date=first_date,
            evidence_items=evidence_items,
        )
        edge_count += 1

        # 更新 org 日期范围
        for name in [src, dst]:
            if G.nodes[name].get("node_type") == "organization" and first_date:
                org_date_ranges[name].append(first_date)

    # 回填 org 的 first_seen / last_seen
    for name, dates in org_date_ranges.items():
        if name in G.nodes:
            ds = sorted(dates)
            G.nodes[name]["first_seen"] = ds[0]
            G.nodes[name]["last_seen"]  = ds[-1]

    print(f"关系边: {edge_count}")
    print(f"图谱总节点: {G.number_of_nodes()}，总边: {G.number_of_edges()}")
    return G


def export_json(G: nx.DiGraph, path: Path):
    """导出为 D3.js 标准格式 {nodes, links}"""
    nodes = []
    for name, data in G.nodes(data=True):
        node = {"id": name, **data}
        # 计算无向度（入度 + 出度，去重）
        node["degree"] = G.degree(name)
        nodes.append(node)

    links = []
    for src, dst, data in G.edges(data=True):
        links.append({"source": src, "target": dst, **data})

    graph_data = {
        "nodes": nodes,
        "links": links,
        "meta": {
            "node_count": len(nodes),
            "link_count": len(links),
            "node_types": _count_by(nodes, "node_type"),
        }
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    print(f"图谱 JSON 已写入: {path}")


def _count_by(items, key):
    counter = defaultdict(int)
    for item in items:
        counter[item.get(key, "unknown")] += 1
    return dict(counter)


def main():
    print("构建知识图谱...")
    G = build_graph()
    export_json(G, GRAPH_DIR / "graph.json")
    print("完成。")


if __name__ == "__main__":
    main()
