from __future__ import annotations

import logging
from dataclasses import dataclass, field
from statistics import mean

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GraphMetrics:
    """Structural metrics computed over a simple undirected view of the graph."""

    label: str
    nodes: int
    edges: int
    dishes: int
    ingredients: int
    density: float
    avg_degree: float
    components: int
    largest_component_size: int
    diameter_lcc: int | None
    avg_shortest_path_lcc: float | None
    avg_clustering: float
    transitivity: float
    top_degree: list[tuple[str, int]] = field(default_factory=list)
    top_betweenness: list[tuple[str, float]] = field(default_factory=list)
    top_closeness: list[tuple[str, float]] = field(default_factory=list)
    top_eigenvector: list[tuple[str, float]] = field(default_factory=list)
    top_pagerank: list[tuple[str, float]] = field(default_factory=list)


@dataclass(frozen=True)
class ComparativeReport:
    """Side-by-side view of Bambu and Camarões plus their shared ingredients."""

    whole: GraphMetrics
    bambu: GraphMetrics
    camaroes: GraphMetrics
    shared_ingredients: list[str]
    only_bambu: list[str]
    only_camaroes: list[str]
    jaccard: float


def simplify(graph: nx.MultiDiGraph) -> nx.Graph:
    """Collapse the MultiDiGraph to a simple undirected graph for structural metrics."""
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes(data=True))
    for u, v in graph.edges():
        if u != v:
            simple.add_edge(u, v)
    return simple


def restaurant_subgraph(graph: nx.MultiDiGraph, restaurant: str) -> nx.MultiDiGraph:
    """Return the subgraph of dishes from one restaurant plus their ingredients."""
    dishes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "Prato" and data.get("restaurant") == restaurant
    ]
    ingredients = {neighbor for dish in dishes for neighbor in graph.neighbors(dish)}
    return graph.subgraph([*dishes, *ingredients]).copy()


def compute_metrics(graph: nx.MultiDiGraph, label: str, *, top_k: int = 10) -> GraphMetrics:
    """Compute the course metrics (density, components, diameter, clustering, …)."""
    simple = simplify(graph)
    dishes = [n for n, d in simple.nodes(data=True) if d.get("type") == "Prato"]
    ingredients = [n for n, d in simple.nodes(data=True) if d.get("type") == "Ingrediente"]

    degrees = [deg for _, deg in simple.degree()]
    avg_deg = mean(degrees) if degrees else 0.0

    components = list(nx.connected_components(simple))
    lcc_nodes = max(components, key=len) if components else set()
    lcc = simple.subgraph(lcc_nodes).copy()

    diameter = nx.diameter(lcc) if lcc.number_of_nodes() > 1 else None
    avg_path = nx.average_shortest_path_length(lcc) if lcc.number_of_nodes() > 1 else None

    top_degree = sorted(simple.degree(), key=lambda pair: pair[1], reverse=True)[:top_k]
    top_bet, top_close, top_eigen, top_pr = _centralities_on_lcc(lcc, top_k)

    return GraphMetrics(
        label=label,
        nodes=simple.number_of_nodes(),
        edges=simple.number_of_edges(),
        dishes=len(dishes),
        ingredients=len(ingredients),
        density=nx.density(simple),
        avg_degree=avg_deg,
        components=len(components),
        largest_component_size=len(lcc_nodes),
        diameter_lcc=diameter,
        avg_shortest_path_lcc=avg_path,
        avg_clustering=nx.average_clustering(simple),
        transitivity=nx.transitivity(simple),
        top_degree=top_degree,
        top_betweenness=top_bet,
        top_closeness=top_close,
        top_eigenvector=top_eigen,
        top_pagerank=top_pr,
    )


def _centralities_on_lcc(
    lcc: nx.Graph, top_k: int
) -> tuple[
    list[tuple[str, float]],
    list[tuple[str, float]],
    list[tuple[str, float]],
    list[tuple[str, float]],
]:
    """Betweenness, closeness, eigenvector and PageRank — computed on the LCC only.

    Eigenvector centrality is numerically fragile on disconnected graphs,
    so we run all four on the largest connected component for consistency.
    """
    if lcc.number_of_nodes() < 2:
        return [], [], [], []

    betweenness = nx.betweenness_centrality(lcc)
    closeness = nx.closeness_centrality(lcc)
    eigenvector = nx.eigenvector_centrality_numpy(lcc)
    pagerank = nx.pagerank(lcc)

    return (
        _top_centrality(betweenness, top_k),
        _top_centrality(closeness, top_k),
        _top_centrality(eigenvector, top_k),
        _top_centrality(pagerank, top_k),
    )


def _top_centrality(scores: dict[str, float], top_k: int) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]


def compare_ingredients(graph: nx.MultiDiGraph) -> tuple[set[str], set[str], set[str]]:
    """Return (shared, only_bambu, only_camaroes) ingredient sets."""
    bambu = _ingredients_of(graph, "Bambu")
    camaroes = _ingredients_of(graph, "Camarões")
    return bambu & camaroes, bambu - camaroes, camaroes - bambu


def build_report(graph: nx.MultiDiGraph) -> ComparativeReport:
    """Compute whole-graph and per-restaurant metrics plus ingredient overlap."""
    bambu_graph = restaurant_subgraph(graph, "Bambu")
    camaroes_graph = restaurant_subgraph(graph, "Camarões")
    shared, only_bambu, only_camaroes = compare_ingredients(graph)
    union = shared | only_bambu | only_camaroes
    jaccard = len(shared) / len(union) if union else 0.0

    return ComparativeReport(
        whole=compute_metrics(graph, label="Geral"),
        bambu=compute_metrics(bambu_graph, label="Bambu"),
        camaroes=compute_metrics(camaroes_graph, label="Camarões"),
        shared_ingredients=sorted(shared),
        only_bambu=sorted(only_bambu),
        only_camaroes=sorted(only_camaroes),
        jaccard=jaccard,
    )


def format_report(report: ComparativeReport) -> str:
    """Render the comparative report as a human-readable text block."""
    lines: list[str] = []
    for metrics in (report.whole, report.bambu, report.camaroes):
        lines.extend(_format_metrics(metrics))
        lines.append("")

    lines.append("== Sobreposição de ingredientes ==")
    lines.append(f"Compartilhados : {len(report.shared_ingredients)}")
    lines.append(f"Só no Bambu    : {len(report.only_bambu)}")
    lines.append(f"Só no Camarões : {len(report.only_camaroes)}")
    lines.append(f"Jaccard        : {report.jaccard:.3f}")
    if report.shared_ingredients:
        lines.append(f"  shared      : {', '.join(report.shared_ingredients)}")
    if report.only_bambu:
        lines.append(f"  só Bambu    : {', '.join(report.only_bambu)}")
    if report.only_camaroes:
        lines.append(f"  só Camarões : {', '.join(report.only_camaroes)}")
    return "\n".join(lines)


def _format_metrics(m: GraphMetrics) -> list[str]:
    diameter = "n/d" if m.diameter_lcc is None else str(m.diameter_lcc)
    avg_path = "n/d" if m.avg_shortest_path_lcc is None else f"{m.avg_shortest_path_lcc:.3f}"
    return [
        f"== {m.label} ==",
        f"Nós            : {m.nodes}  (pratos={m.dishes}, ingredientes={m.ingredients})",
        f"Arestas        : {m.edges}",
        f"Densidade      : {m.density:.4f}",
        f"Grau médio     : {m.avg_degree:.3f}",
        f"Componentes    : {m.components}  (maior = {m.largest_component_size} nós)",
        f"Diâmetro (LCC) : {diameter}",
        f"Caminho médio  : {avg_path}",
        f"Clustering méd : {m.avg_clustering:.4f}",
        f"Transitividade : {m.transitivity:.4f}",
        f"Top grau       : {_fmt_pairs(m.top_degree, int_values=True)}",
        f"Top betweenness: {_fmt_pairs(m.top_betweenness)}",
        f"Top closeness  : {_fmt_pairs(m.top_closeness)}",
        f"Top eigenvector: {_fmt_pairs(m.top_eigenvector)}",
        f"Top pagerank   : {_fmt_pairs(m.top_pagerank)}",
    ]


def _fmt_pairs(pairs: list[tuple[str, float]], *, int_values: bool = False) -> str:
    if not pairs:
        return "n/d"
    if int_values:
        return ", ".join(f"{name} ({int(value)})" for name, value in pairs)
    return ", ".join(f"{name} ({value:.3f})" for name, value in pairs)


def _ingredients_of(graph: nx.MultiDiGraph, restaurant: str) -> set[str]:
    dishes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "Prato" and data.get("restaurant") == restaurant
    ]
    return {
        neighbor
        for dish in dishes
        for neighbor in graph.neighbors(dish)
        if graph.nodes[neighbor].get("type") == "Ingrediente"
    }
