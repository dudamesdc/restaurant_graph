from __future__ import annotations

import logging
from dataclasses import dataclass

import spacy

from .ingredients import INGREDIENTS, RELATION_KEYWORDS

logger = logging.getLogger(__name__)

_ENTITY_LABEL = "INGREDIENTE"


@dataclass(frozen=True)
class IngredientMention:
    text: str


@dataclass(frozen=True)
class IngredientRelation:
    source: str
    target: str
    label: str


class IngredientNER:
    """spaCy-backed NER that tags ingredients and extracts typed relations."""

    def __init__(self) -> None:
        logger.info("loading spaCy model pt_core_news_lg")
        self.nlp = spacy.load("pt_core_news_lg")

        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": _ENTITY_LABEL, "pattern": name}
            for names in INGREDIENTS.values()
            for name in names
        ]
        ruler.add_patterns(patterns)
        logger.info("loaded %d ingredient patterns", len(patterns))

    def extract(self, text: str) -> tuple[list[IngredientMention], list[IngredientRelation]]:
        doc = self.nlp(text.lower())
        entities = [ent for ent in doc.ents if ent.label_ == _ENTITY_LABEL]

        # Deduplicate by text while preserving first-seen order. The
        # original code used set(entities), which is unreliable for spaCy
        # Span objects (two spans over the same word are distinct objects).
        seen: set[str] = set()
        mentions: list[IngredientMention] = []
        for ent in entities:
            name = _normalize_name(ent.text)
            if name in seen:
                continue
            seen.add(name)
            mentions.append(IngredientMention(text=name))

        relations: list[IngredientRelation] = []
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1, e2 = entities[i], entities[j]
                span_between = doc[e1.end : e2.start].text.strip()

                label = _classify_span(span_between)
                if label is None:
                    continue
                
                src = _normalize_name(e1.text)
                tgt = _normalize_name(e2.text)
                relations.append(IngredientRelation(source=src, target=tgt, label=label))

        return mentions, relations


def _classify_span(span_between: str) -> str | None:
    """Return a relation label when a keyword appears between two mentions, else None.

    Unlike the earlier heuristic, no default relation is emitted — we only
    connect two ingredient mentions when the description explicitly carries
    a relation keyword. Dish→ingredient membership is still recorded as a
    CONTÉM edge at the graph layer, so the bipartite projection remains
    intact.
    """
    for label, keywords in RELATION_KEYWORDS.items():
        if any(keyword in span_between for keyword in keywords):
            return label
    return None


def _normalize_name(name: str) -> str:
    """Apply manual normalization rules per user request."""
    if name == "camarões":
        return "camarão"
    return name
