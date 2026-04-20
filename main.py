from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

from graph import build_graph
from viz import render_interactive, render_static

ROOT = Path(__file__).resolve().parent
MENU_FILES = [
    ROOT / "json_graphs" / "bambu.json",
    ROOT / "json_graphs" / "camaroes.json",
]
OUTPUT_DIR = ROOT / "outputs"
GRAPH_FILE = OUTPUT_DIR / "restaurant_graph.gexf"
STATIC_FILE = OUTPUT_DIR / "graph_static.png"
INTERACTIVE_FILE = OUTPUT_DIR / "graph_interactive.html"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    OUTPUT_DIR.mkdir(exist_ok=True)

    graph = build_graph(MENU_FILES)
    nx.write_gexf(graph, GRAPH_FILE)

    render_static(GRAPH_FILE, STATIC_FILE)
    render_interactive(GRAPH_FILE, INTERACTIVE_FILE)

    nodes, edges = graph.number_of_nodes(), graph.number_of_edges()
    print(f"Graph:       {GRAPH_FILE}  ({nodes} nodes, {edges} edges)")
    print(f"Static:      {STATIC_FILE}")
    print(f"Interactive: {INTERACTIVE_FILE}")


if __name__ == "__main__":
    main()
