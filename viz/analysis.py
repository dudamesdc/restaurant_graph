from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from graph.analysis import ComparativeReport, RandomBaseline

from ._palette import COLOR_BAMBU, COLOR_CAMAROES, ingredient_color

logger = logging.getLogger(__name__)


def render_degree_distribution(
    graph: nx.MultiDiGraph,
    output_file: Path,
    *,
    dpi: int = 160,
) -> None:
    """Plot the degree distribution on a log-log scale (whole graph)."""
    simple = _simple_view(graph)
    degrees = [deg for _, deg in simple.degree() if deg > 0]
    counts = Counter(degrees)
    xs = sorted(counts)
    ys = [counts[x] for x in xs]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(xs, ys, marker="o", linestyle="", color="#264653")
    ax.set_xlabel("Grau k (log)")
    ax.set_ylabel("Número de nós com grau k (log)")
    ax.set_title("Distribuição de grau — grafo completo")
    ax.grid(True, which="both", alpha=0.3)
    _save(fig, output_file, dpi)


def render_ingredient_comparison(
    report: ComparativeReport,
    output_file: Path,
    *,
    dpi: int = 160,
) -> None:
    """Bar chart comparing unique vs shared ingredients between restaurants."""
    labels = ["Só Bambu", "Compartilhados", "Só Camarões"]
    values = [len(report.only_bambu), len(report.shared_ingredients), len(report.only_camaroes)]
    colors = [COLOR_BAMBU, "#8d99ae", COLOR_CAMAROES]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
            fontsize=10,
        )
    ax.set_ylabel("Ingredientes distintos")
    ax.set_title(
        f"Ingredientes: Bambu vs Camarões — Jaccard = {report.jaccard:.3f}",
    )
    _save(fig, output_file, dpi)


def render_shared_ingredients_network(
    graph: nx.MultiDiGraph,
    report: ComparativeReport,
    output_file: Path,
    *,
    top_n: int = 12,
    dpi: int = 200,
) -> None:
    """Draw the bipartite subgraph of the N most-shared ingredients and their dishes."""
    simple = _simple_view(graph)
    shared_by_degree = sorted(
        (ing for ing in report.shared_ingredients if ing in simple),
        key=lambda n: simple.degree(n),
        reverse=True,
    )[:top_n]

    if not shared_by_degree:
        logger.warning("no shared ingredients with degree > 0 — skipping %s", output_file)
        return

    dishes = {
        neighbor
        for ing in shared_by_degree
        for neighbor in simple.neighbors(ing)
        if simple.nodes[neighbor].get("type") == "Prato"
    }
    subgraph = simple.subgraph([*shared_by_degree, *dishes]).copy()

    positions = nx.spring_layout(subgraph, k=0.6, iterations=80, seed=42)

    fig, ax = plt.subplots(figsize=(12, 9))
    nx.draw_networkx_edges(subgraph, positions, alpha=0.25, edge_color="gray", ax=ax)

    dish_nodes = [n for n in subgraph if subgraph.nodes[n].get("type") == "Prato"]
    ingredient_nodes = [n for n in subgraph if subgraph.nodes[n].get("type") == "Ingrediente"]
    dish_colors = [
        COLOR_BAMBU if subgraph.nodes[n].get("restaurant") == "Bambu" else COLOR_CAMAROES
        for n in dish_nodes
    ]
    ingredient_colors = [
        ingredient_color(subgraph.nodes[n].get("category")) for n in ingredient_nodes
    ]

    nx.draw_networkx_nodes(
        subgraph, positions, nodelist=dish_nodes, node_color=dish_colors, node_size=120, ax=ax
    )
    nx.draw_networkx_nodes(
        subgraph,
        positions,
        nodelist=ingredient_nodes,
        node_color=ingredient_colors,
        node_size=600,
        edgecolors="black",
        linewidths=1.2,
        ax=ax,
    )
    nx.draw_networkx_labels(
        subgraph,
        positions,
        labels={n: n for n in ingredient_nodes},
        font_size=10,
        font_weight="bold",
        ax=ax,
    )
    ax.set_title(f"Top {len(shared_by_degree)} ingredientes compartilhados e seus pratos")
    ax.axis("off")
    _save(fig, output_file, dpi)


def render_random_comparison(
    baselines: list[RandomBaseline],
    output_file: Path,
    *,
    dpi: int = 160,
) -> None:
    """Side-by-side bars comparing real vs ER vs WS on clustering and avg path."""
    if not baselines:
        logger.warning("no random baselines to plot — skipping %s", output_file)
        return

    names = [b.name for b in baselines]
    clusterings = [b.clustering for b in baselines]
    paths = [b.avg_path if b.avg_path is not None else 0.0 for b in baselines]
    colors = ["#264653", "#e9c46a", "#2a9d8f"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    bars1 = ax1.bar(names, clusterings, color=colors)
    ax1.set_title("Clustering médio")
    ax1.set_ylabel("C")
    for bar, value in zip(bars1, clusterings, strict=True):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    bars2 = ax2.bar(names, paths, color=colors)
    ax2.set_title("Caminho médio na LCC")
    ax2.set_ylabel("L")
    for bar, value in zip(bars2, paths, strict=True):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.suptitle("Rede real vs. grafos aleatórios (ER / Watts-Strogatz)")
    _save(fig, output_file, dpi)


def _simple_view(graph: nx.MultiDiGraph) -> nx.Graph:
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes(data=True))
    for u, v in graph.edges():
        if u != v:
            simple.add_edge(u, v)
    return simple


def _save(fig: plt.Figure, output_file: Path, dpi: int) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_file, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("wrote %s", output_file)
