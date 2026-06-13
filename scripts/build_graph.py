"""Build a force-directed knowledge-graph visualization from the registry.

Outputs:
  visuals/graph.svg          — static high-quality force-directed graph
                               (every entry as a node, adjacency edges,
                                category-colored, node-size by degree)
  visuals/graph-data.json    — the nodes + edges + metadata payload
                               used by the interactive HTML viewer
                               (consumed by visuals/index.html)
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import yaml
from adjustText import adjust_text

REPO = Path(__file__).resolve().parent.parent
REG = REPO / "registry"
OUT_SVG = REPO / "visuals" / "graph.svg"
OUT_JSON = REPO / "visuals" / "graph-data.json"

# BRAND palette (mirrors harmless-harnesses + taxonomy.svg).
CAT_COLOR = {
    "governance": "#1f3a5f",
    "agent":      "#d68910",
    "eval":       "#28a745",
    "redteam":    "#c0392b",
    "routing":    "#3498db",
    "education":  "#7d3c98",
}
CAT_ORDER = ["governance", "agent", "eval", "redteam", "routing", "education"]


def load_entries() -> list[dict]:
    entries = []
    for path in REG.rglob("*.yaml"):
        if path.name in ("_schema.yaml", "_TEMPLATE.yaml"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data:
            entries.append(data)
    return entries


def build_graph(entries: list[dict]) -> nx.Graph:
    G = nx.Graph()
    by_id = {e["id"]: e for e in entries}
    for e in entries:
        maint = e.get("maintainer") or {}
        G.add_node(
            e["id"],
            name=e.get("name", e["id"]),
            category=e["category"],
            subcategory=e.get("subcategory", ""),
            url=e.get("repo_url", ""),
            tagline=e.get("tagline", "")[:240],
            mas=e.get("model_agnostic_score", 3),
            license=e.get("license", ""),
            primary_language=e.get("primary_language", ""),
            maturity=e.get("maturity", ""),
            origin_country=e.get("origin_country") or "",
            maintainer_type=maint.get("type", "") if isinstance(maint, dict) else "",
            maintainer_name=maint.get("name", "") if isinstance(maint, dict) else "",
            harness_alignment=e.get("harness_paradigm_alignment", ""),
        )
    for e in entries:
        for tgt in e.get("adjacent_to", []) or []:
            if tgt in by_id:
                G.add_edge(e["id"], tgt)
    return G


def main() -> int:
    entries = load_entries()
    G = build_graph(entries)
    print(f"loaded {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Force-directed layout. Higher k = more spread; seed for reproducibility.
    pos = nx.spring_layout(G, seed=42, k=0.55, iterations=180, weight=None)

    # Node attributes for drawing.
    degrees = dict(G.degree())
    max_d = max(degrees.values()) if degrees else 1
    node_colors = [CAT_COLOR[G.nodes[n]["category"]] for n in G.nodes]
    node_sizes = [80 + (degrees[n] / max_d) * 720 for n in G.nodes]

    # --- Static SVG ---
    fig, ax = plt.subplots(figsize=(20, 15), dpi=120)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    fig.subplots_adjust(top=0.92, bottom=0.04, left=0.02, right=0.98)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=0.5, alpha=0.15, edge_color="#1f3a5f",
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        linewidths=0.7, edgecolors="#ffffff",
        alpha=0.93,
    )

    # Label only the top-degree nodes per category. adjustText pushes labels
    # away from overlap and draws short leader-lines.
    label_count_per_cat = {"governance": 4, "agent": 5, "eval": 5,
                           "redteam": 4, "routing": 5, "education": 4}
    by_cat = defaultdict(list)
    for n in G.nodes:
        by_cat[G.nodes[n]["category"]].append(n)
    texts = []
    for cat, ids in by_cat.items():
        ids.sort(key=lambda i: degrees[i], reverse=True)
        for nid in ids[:label_count_per_cat[cat]]:
            x, y = pos[nid]
            nm = G.nodes[nid]["name"]
            display = nm if len(nm) <= 32 else nm[:30] + "…"
            texts.append(ax.text(
                x, y, display,
                fontsize=10, fontweight="700", color="#0d1f33",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.28", facecolor="#ffffff",
                          edgecolor=CAT_COLOR[cat], alpha=0.95, linewidth=0.9),
                zorder=10,
            ))
    adjust_text(
        texts,
        ax=ax,
        expand=(1.2, 1.4),
        force_text=(0.4, 0.6),
        force_static=(0.2, 0.3),
        arrowprops=dict(arrowstyle="-", color="#4a5d75", lw=0.5, alpha=0.7),
    )

    # Title + subtitle at the figure level so they aren't clipped.
    fig.suptitle(
        f"open-harness-atlas — knowledge graph "
        f"({G.number_of_nodes()} entries · {G.number_of_edges()} adjacency edges)",
        fontsize=17, color="#1f3a5f", weight="bold", x=0.02, ha="left", y=0.975,
    )
    fig.text(
        0.02, 0.945,
        "Force-directed layout. Node size = degree (neighbours in the graph). "
        "Edge = explicit adjacent_to. Auto-generated from registry/*/*.yaml.",
        fontsize=10.5, color="#4a5d75", ha="left",
    )

    # Legend.
    legend_handles = []
    cat_counts = {c: 0 for c in CAT_ORDER}
    for n in G.nodes:
        cat_counts[G.nodes[n]["category"]] += 1
    for cat in CAT_ORDER:
        legend_handles.append(
            plt.Line2D([0], [0], marker="o", color="w",
                       markerfacecolor=CAT_COLOR[cat], markersize=10,
                       label=f"{cat} ({cat_counts[cat]})")
        )
    ax.legend(handles=legend_handles, loc="lower right",
              frameon=True, fontsize=10, framealpha=0.95,
              edgecolor="#d8e1eb", facecolor="#ffffff",
              title="Category (count)", title_fontsize=10)

    ax.set_axis_off()
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_SVG, format="svg",
                facecolor="#ffffff", edgecolor="none")
    out_png = OUT_SVG.with_suffix(".png")
    fig.savefig(out_png, format="png", dpi=140,
                facecolor="#ffffff", edgecolor="none")
    plt.close(fig)
    print(f"wrote {OUT_SVG.relative_to(REPO)}")
    print(f"wrote {out_png.relative_to(REPO)}")

    # --- JSON payload for the interactive HTML viewer ---
    # Compute aggregate stats for the sidebar.
    top_hubs = sorted(degrees.items(), key=lambda x: -x[1])[:12]
    lic_counts: dict[str, int] = defaultdict(int)
    mat_counts: dict[str, int] = defaultdict(int)
    country_counts: dict[str, int] = defaultdict(int)
    lang_counts: dict[str, int] = defaultdict(int)
    mas_counts: dict[int, int] = defaultdict(int)
    for n in G.nodes:
        lic_counts[G.nodes[n].get("license") or "Unknown"] += 1
        mat_counts[G.nodes[n].get("maturity") or "Unknown"] += 1
        country_counts[G.nodes[n].get("origin_country") or "Unknown"] += 1
        lang_counts[G.nodes[n].get("primary_language") or "Unknown"] += 1
        mas_counts[G.nodes[n].get("mas", 3)] += 1

    payload = {
        "meta": {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "avg_degree": (
                round(sum(degrees.values()) / max(len(degrees), 1), 2)
            ),
            "density": round(nx.density(G), 4),
            "categories": [
                {"key": c, "color": CAT_COLOR[c], "count": cat_counts[c]}
                for c in CAT_ORDER
            ],
            "top_hubs": [
                {
                    "id": nid,
                    "name": G.nodes[nid]["name"],
                    "category": G.nodes[nid]["category"],
                    "degree": d,
                }
                for nid, d in top_hubs
            ],
            "licenses":  sorted(lic_counts.items(),     key=lambda x: -x[1]),
            "maturity":  sorted(mat_counts.items(),     key=lambda x: -x[1]),
            "countries": sorted(country_counts.items(), key=lambda x: -x[1]),
            "languages": sorted(lang_counts.items(),    key=lambda x: -x[1]),
            "mas":       sorted(mas_counts.items(),     key=lambda x: x[0]),
        },
        "nodes": [
            {
                "id": n,
                "name": G.nodes[n]["name"],
                "category": G.nodes[n]["category"],
                "subcategory": G.nodes[n].get("subcategory", ""),
                "color": CAT_COLOR[G.nodes[n]["category"]],
                "url": G.nodes[n]["url"],
                "tagline": G.nodes[n]["tagline"],
                "degree": degrees[n],
                "mas": G.nodes[n]["mas"],
                "license": G.nodes[n].get("license", ""),
                "language": G.nodes[n].get("primary_language", ""),
                "maturity": G.nodes[n].get("maturity", ""),
                "country": G.nodes[n].get("origin_country", ""),
                "maintainer_type": G.nodes[n].get("maintainer_type", ""),
                "maintainer_name": G.nodes[n].get("maintainer_name", ""),
                "alignment": G.nodes[n].get("harness_alignment", ""),
            }
            for n in G.nodes
        ],
        "links": [{"source": s, "target": t} for s, t in G.edges],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
