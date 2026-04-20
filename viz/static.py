from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

from ._palette import (
    COLOR_BAMBU,
    COLOR_CAMAROES,
    COLOR_INGREDIENT,
    dish_color,
    ingredient_color,
)

logger = logging.getLogger(__name__)


def render_static(
    graph_file: Path,
    output_file: Path,
    *,
    figsize: tuple[int, int] = (16, 16),
    label_degree_threshold: int = 8,
    dpi: int = 200,
) -> None:
    """Render a GEXF graph as a static PNG figure.

    Dishes are coloured by restaurant, ingredients by taxonomy category,
    so a single picture makes the pratos↔ingredientes bipartition and the
    Bambu-vs-Camarões split visually obvious.
    """
    logger.info("loading %s", graph_file)
    graph = nx.read_gexf(graph_file)

    dishes = [n for n, d in graph.nodes(data=True) if d.get("type") == "Prato"]
    ingredients = [n for n, d in graph.nodes(data=True) if d.get("type") == "Ingrediente"]

    dish_colors = [dish_color(graph.nodes[n].get("restaurant", "")) for n in dishes]
    ingredient_colors = [ingredient_color(graph.nodes[n].get("category")) for n in ingredients]

    logger.info("computing spring layout on %d nodes", graph.number_of_nodes())
    positions = nx.spring_layout(graph, k=0.15, iterations=50, seed=42)

    plt.figure(figsize=figsize)
    nx.draw_networkx_edges(graph, positions, alpha=0.1, edge_color="gray")
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=dishes,
        node_color=dish_colors,
        node_size=90,
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=ingredients,
        node_color=ingredient_colors,
        node_size=30,
        alpha=0.8,
    )

    hubs = {n: n for n in dishes if graph.degree(n) > label_degree_threshold}
    nx.draw_networkx_labels(graph, positions, hubs, font_size=8)

    plt.legend(
        handles=_legend_handles(),
        loc="upper left",
        fontsize=9,
        frameon=True,
    )
    plt.title("Rede de Pratos e Ingredientes — Bambu vs. Camarões")
    plt.axis("off")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    plt.close()
    logger.info("wrote static graph to %s", output_file)


def _legend_handles() -> list[Line2D]:
    dish_entries = [
        ("Prato — Bambu", COLOR_BAMBU),
        ("Prato — Camarões", COLOR_CAMAROES),
    ]
    ingredient_entries = [
        (f"Ingrediente — {category.replace('_', ' ').title()}", color)
        for category, color in COLOR_INGREDIENT.items()
    ]
    return [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            color=color,
            label=label,
            markersize=8,
        )
        for label, color in (*dish_entries, *ingredient_entries)
    ]
