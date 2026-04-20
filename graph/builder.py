from __future__ import annotations

import json
import logging
from pathlib import Path

import networkx as nx

from .ingredients import INGREDIENT_CATEGORY
from .ner import IngredientNER

logger = logging.getLogger(__name__)


def build_graph(sources: list[Path]) -> nx.MultiDiGraph:
    """Build a dish-ingredient graph from the given menu JSON files."""
    ner = IngredientNER()
    graph = nx.MultiDiGraph()

    for source in sources:
        restaurant = _restaurant_of(source)
        logger.info("processing %s (restaurant=%s)", source, restaurant)

        with source.open(encoding="utf-8") as f:
            items = json.load(f)

        for item in items:
            dish = item.get("prato")
            description = item.get("descricao")
            if not dish or not description:
                continue

            graph.add_node(
                dish,
                type="Prato",
                category=item.get("categoria") or "N/A",
                price=item.get("preco") or "Consultar",
                restaurant=restaurant,
            )

            mentions, relations = ner.extract(description)

            for mention in mentions:
                graph.add_node(
                    mention.text,
                    type="Ingrediente",
                    category=INGREDIENT_CATEGORY.get(mention.text, "OUTRO"),
                )
                graph.add_edge(dish, mention.text, relation="CONTÉM")

            for relation in relations:
                graph.add_edge(relation.source, relation.target, relation=relation.label)

    logger.info(
        "graph built: %d nodes, %d edges",
        graph.number_of_nodes(),
        graph.number_of_edges(),
    )
    return graph


def _restaurant_of(source: Path) -> str:
    stem = source.stem.lower()
    if "bambu" in stem:
        return "Bambu"
    if "camaroes" in stem:
        return "Camarões"
    return "Desconhecido"
