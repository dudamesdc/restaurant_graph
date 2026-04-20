from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

from graph import build_graph, build_report, format_report
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
GRAPH_FILE = OUTPUT_DIR / "restaurant_graph.gexf"
STATIC_FILE = OUTPUT_DIR / "graph_static.png"
INTERACTIVE_FILE = OUTPUT_DIR / "graph_interactive.html"
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

    render_static(GRAPH_FILE, STATIC_FILE)
    render_interactive(GRAPH_FILE, INTERACTIVE_FILE)

    report = build_report(graph)
    METRICS_FILE.write_text(format_report(report), encoding="utf-8")
    render_degree_distribution(graph, DEGREE_PLOT)
    render_ingredient_comparison(report, INGREDIENT_PLOT)
    render_shared_ingredients_network(graph, report, SHARED_PLOT)
    render_random_comparison(report.random_baselines, RANDOM_PLOT)

    render_dashboard(
        report,
        DashboardAssets(
            static_png=STATIC_FILE.relative_to(OUTPUT_DIR).as_posix(),
            interactive_html=INTERACTIVE_FILE.relative_to(OUTPUT_DIR).as_posix(),
            degree_plot=DEGREE_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            ingredient_plot=INGREDIENT_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            shared_plot=SHARED_PLOT.relative_to(OUTPUT_DIR).as_posix(),
            random_plot=RANDOM_PLOT.relative_to(OUTPUT_DIR).as_posix(),
        ),
        DASHBOARD_FILE,
    )

    nodes, edges = graph.number_of_nodes(), graph.number_of_edges()
    print(f"Graph:       {GRAPH_FILE}  ({nodes} nodes, {edges} edges)")
    print(f"Static:      {STATIC_FILE}")
    print(f"Interactive: {INTERACTIVE_FILE}")
    print(f"Metrics:     {METRICS_FILE}")
    print(f"Analysis:    {ANALYSIS_DIR}")
    print(f"Dashboard:   {DASHBOARD_FILE}")


if __name__ == "__main__":
    main()
