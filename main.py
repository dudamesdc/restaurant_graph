from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

from graph import build_graph

ROOT = Path(__file__).resolve().parent
MENU_FILES = [
    ROOT / "json_graphs" / "bambu.json",
    ROOT / "json_graphs" / "camaroes.json",
]
OUTPUT_FILE = ROOT / "restaurant_graph.gexf"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    graph = build_graph(MENU_FILES)
    nx.write_gexf(graph, OUTPUT_FILE)

    print(f"Graph saved to {OUTPUT_FILE}")
    print(f"  nodes: {graph.number_of_nodes()}")
    print(f"  edges: {graph.number_of_edges()}")


if __name__ == "__main__":
    main()
