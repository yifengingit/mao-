#!/usr/bin/env python3
"""
知识图谱分析脚本

对已构建的图谱运行中心度计算和社群检测，结果写回 graph.json 的节点属性。

用法：
    python scripts/analyze_graph.py
"""

import json
from pathlib import Path

import community as community_louvain
import networkx as nx

PROJECT_ROOT = Path(__file__).parent.parent
GRAPH_DIR    = PROJECT_ROOT / "data" / "index" / "graph"
GRAPH_FILE   = GRAPH_DIR / "graph.json"


def load_graph_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_graph_json(data: dict, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_nx_from_json(graph_data: dict) -> nx.Graph:
    """从 graph.json 重建 NetworkX 无向图（分析用）"""
    G = nx.Graph()
    for node in graph_data["nodes"]:
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for link in graph_data["links"]:
        G.add_edge(link["source"], link["target"],
                   weight=link.get("confidence", 1.0),
                   relation_type=link.get("relation_type", ""))
    return G


def normalize(values: dict) -> dict:
    """Min-max 归一化到 [0, 1]"""
    if not values:
        return values
    vmin = min(values.values())
    vmax = max(values.values())
    if vmax == vmin:
        return {k: 0.5 for k in values}
    return {k: (v - vmin) / (vmax - vmin) for k, v in values.items()}


def analyze(graph_data: dict) -> dict:
    G = build_nx_from_json(graph_data)
    print(f"图谱规模: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")

    # ── 度中心度 ─────────────────────────────────────────────────
    print("计算度中心度...")
    degree_centrality = nx.degree_centrality(G)

    # ── 介数中心度（大图较慢，加 k 采样近似） ──────────────────────
    print("计算介数中心度（采样近似）...")
    n = G.number_of_nodes()
    k = min(n, 200)  # 采样节点数，平衡速度与精度
    betweenness = nx.betweenness_centrality(G, k=k, normalized=True)

    # ── 归一化（方便前端按大小编码） ──────────────────────────────
    degree_norm     = normalize(degree_centrality)
    betweenness_norm = normalize(betweenness)

    # ── 社群检测（Louvain） ──────────────────────────────────────
    print("运行 Louvain 社群检测...")
    partition = community_louvain.best_partition(G, weight="weight", random_state=42)
    num_communities = len(set(partition.values()))
    print(f"  检测到 {num_communities} 个社群")

    # ── 社群规模统计 ─────────────────────────────────────────────
    community_sizes = {}
    for node, cid in partition.items():
        community_sizes[cid] = community_sizes.get(cid, 0) + 1

    # 按规模降序，给社群重新编号（0 = 最大社群）
    sorted_cids = sorted(community_sizes, key=community_sizes.__getitem__, reverse=True)
    cid_remap = {old: new for new, old in enumerate(sorted_cids)}
    partition_remapped = {node: cid_remap[cid] for node, cid in partition.items()}

    # ── 写回节点属性 ─────────────────────────────────────────────
    node_index = {n["id"]: n for n in graph_data["nodes"]}
    for name in G.nodes():
        node = node_index.get(name)
        if not node:
            continue
        node["degree_centrality"]      = round(degree_centrality.get(name, 0), 4)
        node["betweenness_centrality"] = round(betweenness.get(name, 0), 4)
        node["degree_centrality_norm"] = round(degree_norm.get(name, 0), 4)
        node["betweenness_norm"]       = round(betweenness_norm.get(name, 0), 4)
        node["community_id"]           = partition_remapped.get(name, -1)

    # ── 全局统计写入 meta ────────────────────────────────────────
    graph_data["meta"]["communities"] = num_communities
    graph_data["meta"]["community_sizes"] = {
        str(cid_remap[old]): sz
        for old, sz in sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
    }

    # ── 打印 Top 15 最高介数中心度节点（关键桥梁人物） ────────────
    print("\nTop 15 介数中心度（关键桥梁节点）:")
    top15 = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:15]
    for name, score in top15:
        ntype = node_index.get(name, {}).get("node_type", "?")
        cid   = partition_remapped.get(name, -1)
        print(f"  {name:12s}  betweenness={score:.4f}  type={ntype}  community={cid}")

    return graph_data


def main():
    if not GRAPH_FILE.exists():
        print(f"错误：{GRAPH_FILE} 不存在，请先运行 build_graph.py")
        return

    print("加载图谱...")
    graph_data = load_graph_json(GRAPH_FILE)

    print("开始分析...")
    graph_data = analyze(graph_data)

    save_graph_json(graph_data, GRAPH_FILE)
    print(f"\n分析结果已写回: {GRAPH_FILE}")


if __name__ == "__main__":
    main()
