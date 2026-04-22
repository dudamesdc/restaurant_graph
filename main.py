from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

from graph import build_graph, build_report, format_report, get_lcc_subgraph
from scrapers import regenerate_menus
from viz import (
    DashboardAssets,
    render_dashboard,
    render_degree_distribution,
    render_ingredient_comparison,
    render_interactive,
    render_random_comparison,
    render_shared_ingredients_network,
    render_static,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
MENU_FILES = [
    ROOT / "json_graphs" / "bambu.json",
    ROOT / "json_graphs" / "camaroes.json",
]
OUTPUT_DIR = ROOT / "outputs"
ANALYSIS_DIR = OUTPUT_DIR / "analysis"
GRAPH_FILE = OUTPUT_DIR / "restaurant_graph_full.gexf"
GRAPH_LCC_FILE = OUTPUT_DIR / "restaurant_graph_lcc.gexf"
STATIC_FILE = OUTPUT_DIR / "graph_static.png"
INTERACTIVE_FULL = OUTPUT_DIR / "graph_full.html"
INTERACTIVE_LCC = OUTPUT_DIR / "graph_lcc.html"
INTERACTIVE_SCALED = OUTPUT_DIR / "graph_scaled.html"
METRICS_FILE = ANALYSIS_DIR / "metrics.txt"
DEGREE_PLOT = ANALYSIS_DIR / "degree_distribution.png"
INGREDIENT_PLOT = ANALYSIS_DIR / "ingredient_comparison.png"
SHARED_PLOT = ANALYSIS_DIR / "shared_ingredients_network.png"
RANDOM_PLOT = ANALYSIS_DIR / "random_comparison.png"
DASHBOARD_FILE = OUTPUT_DIR / "index.html"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    OUTPUT_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)

    if any(not menu.exists() for menu in MENU_FILES):
        logger.info("one or more menu JSONs missing — running scrapers first")
        regenerate_menus()

    graph = build_graph(MENU_FILES)
    nx.write_gexf(graph, GRAPH_FILE)

    # Extrair LCC para análise (toda a análise deve considerar apenas a LCC)
    lcc_graph = get_lcc_subgraph(graph)
    nx.write_gexf(lcc_graph, GRAPH_LCC_FILE)

    # Imagem estática do dashboard agora mostra apenas a LCC
    render_static(GRAPH_LCC_FILE, STATIC_FILE)
    
    # Gerar versões do grafo interativo
    render_interactive(GRAPH_FILE, INTERACTIVE_FULL)
    render_interactive(GRAPH_FILE, INTERACTIVE_LCC, filter_lcc=True)
    render_interactive(GRAPH_FILE, INTERACTIVE_SCALED, scale_by_degree=True)

    report = build_report(lcc_graph)
    METRICS_FILE.write_text(format_report(report), encoding="utf-8")
    render_degree_distribution(lcc_graph, DEGREE_PLOT)
    render_ingredient_comparison(report, INGREDIENT_PLOT)
    render_shared_ingredients_network(lcc_graph, report, SHARED_PLOT)
    render_random_comparison(report.random_baselines, RANDOM_PLOT)

    render_dashboard(
        report,
        DashboardAssets(
            static_png=STATIC_FILE.relative_to(OUTPUT_DIR).as_posix(),
            interactive_full=INTERACTIVE_FULL.relative_to(OUTPUT_DIR).as_posix(),
            interactive_lcc=INTERACTIVE_LCC.relative_to(OUTPUT_DIR).as_posix(),
            interactive_scaled=INTERACTIVE_SCALED.relative_to(OUTPUT_DIR).as_posix(),
            degree_plot=DEGREE_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            ingredient_plot=INGREDIENT_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            shared_plot=SHARED_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            random_plot=RANDOM_PLOT.relative_to(OUTPUT_DIR).as_posix(),
        ),
        DASHBOARD_FILE,
    )

    nodes, edges = graph.number_of_nodes(), graph.number_of_edges()
    lcc_nodes, lcc_edges = lcc_graph.number_of_nodes(), lcc_graph.number_of_edges()
    print(f"Graph (Full):   {GRAPH_FILE}  ({nodes} nodes, {edges} edges)")
    print(f"Graph (LCC):    {GRAPH_LCC_FILE}  ({lcc_nodes} nodes, {lcc_edges} edges)")
    print(f"Static:      {STATIC_FILE}")
    print(f"Interactive (Full):   {INTERACTIVE_FULL}")
    print(f"Interactive (LCC):    {INTERACTIVE_LCC}")
    print(f"Interactive (Scaled): {INTERACTIVE_SCALED}")
    print(f"Metrics:     {METRICS_FILE}")
    print(f"Analysis:    {ANALYSIS_DIR}")
    print(f"Dashboard:   {DASHBOARD_FILE}")


if __name__ == "__main__":
    main()
