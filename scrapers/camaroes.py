from __future__ import annotations

import logging
import re
from pathlib import Path

import pdfplumber

from ._types import MenuItem

logger = logging.getLogger(__name__)

# Dish titles on the Camarões PDF are fully uppercase (with optional
# hyphens/slashes) and end on a price token. The price may be a single
# number or two numbers joined by a pipe for two serving sizes — e.g.
# "PASTEL DE CAMARÃO 18 | 26".
_TITLE_PATTERN = re.compile(r"^([A-ZÀ-Ú0-9 \-/]+)\s+((?:\d{2,3}(?:\s*\|\s*\d{2,3})*))$")


def scrape_camaroes(source: Path) -> list[MenuItem]:
    """Extract the Camarões menu from the restaurant's PDF brochure."""
    items: list[MenuItem] = []

    with pdfplumber.open(source) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            items.extend(_parse_page(text))

    logger.info("parsed %d dishes from %s", len(items), source)
    return items


def _parse_page(text: str) -> list[MenuItem]:
    items: list[MenuItem] = []
    current: dict[str, str] | None = None

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        match = _TITLE_PATTERN.match(line)
        if match:
            if current is not None:
                items.append(_finalize(current))
            current = {
                "dish": match.group(1).strip(),
                "price": match.group(2).strip(),
                "description": "",
            }
        elif current is not None:
            current["description"] += line + " "

    if current is not None:
        items.append(_finalize(current))

    return items


def _finalize(buffer: dict[str, str]) -> MenuItem:
    return MenuItem(
        dish=buffer["dish"],
        description=buffer["description"].strip(),
        price=buffer["price"],
    )
