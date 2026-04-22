from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx
from pyvis.network import Network

from ._palette import dish_color, ingredient_color

logger = logging.getLogger(__name__)

_PHYSICS = """
var options = {
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -70,
      "centralGravity": 0.015,
      "springLength": 100,
      "springConstant": 0.08
    },
    "maxVelocity": 50,
    "solver": "forceAtlas2Based",
    "timestep": 0.35,
    "stabilization": {"iterations": 150}
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  }
}
"""


def render_interactive(
    graph_file: Path,
    output_file: Path,
    filter_lcc: bool = False,
    scale_by_degree: bool = False,
) -> None:
    """Render a GEXF graph as an interactive pyvis HTML page."""
    logger.info("loading %s", graph_file)
    graph = nx.read_gexf(graph_file)

    if filter_lcc:
        undirected = graph.to_undirected()
        if undirected.number_of_nodes() > 0:
            lcc_nodes = max(nx.connected_components(undirected), key=len)
            graph = graph.subgraph(lcc_nodes).copy()
            logger.info("filtered to LCC: %d nodes", graph.number_of_nodes())

    degrees = dict(graph.degree())

    net = Network(
        height="100vh",
        width="100%",
        bgcolor="#1a1a1a",
        font_color="white",
        select_menu=True,
        filter_menu=True,
        notebook=False,
        cdn_resources="in_line",
    )

    for node, data in graph.nodes(data=True):
        degree = degrees.get(node, 0)
        color, size, shape = _node_style(data, degree, scale_by_degree)
        net.add_node(
            node,
            label=node,
            title=_hover_text(node, data, degree),
            color=color,
            size=size,
            shape=shape,
        )

    for source, target, data in graph.edges(data=True):
        net.add_edge(
            source,
            target,
            title=data.get("relation", ""),
            color="rgba(150, 150, 150, 0.4)",
        )

    net.set_options(_PHYSICS)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(output_file))
    logger.info("wrote interactive graph to %s", output_file)


def _node_style(data: dict, degree: int = 0, scale_by_degree: bool = False) -> tuple[str, int, str]:
    node_type = data.get("type")
    if node_type == "Prato":
        return dish_color(data.get("restaurant", "")), 20, "dot"
    if node_type == "Ingrediente":
        size = 10
        if scale_by_degree:
            size = 10 + (degree * 2)
        return ingredient_color(data.get("category")), size, "triangle"
    return "#9e9e9e", 15, "box"


def _hover_text(node: str, data: dict, degree: int) -> str:
    parts = [
        f"Nome: {node}",
        f"Tipo: {data.get('type', 'Desconhecido')}",
        f"Grau (Conexões): {degree}",
    ]
    if data.get("type") == "Prato" and data.get("restaurant"):
        parts.append(f"Restaurante: {data['restaurant']}")
    if data.get("category"):
        parts.append(f"Categoria: {data['category']}")
    return "\n".join(parts)
