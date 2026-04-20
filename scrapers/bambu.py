from __future__ import annotations

import logging
from pathlib import Path

from bs4 import BeautifulSoup

from ._types import MenuItem

logger = logging.getLogger(__name__)


def scrape_bambu(source: Path) -> list[MenuItem]:
    """Parse the Coco Bambu online menu from a saved HTML page."""
    html = source.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="text-card-foreground")

    items: list[MenuItem] = []
    for card in cards:
        title_tag = card.find("h6")
        # Cards sharing this class but without an <h6> are layout
        # elements (filters, headers, etc.), not dishes — skip them.
        if title_tag is None:
            continue

        dish = title_tag.get_text(strip=True)

        description_tag = card.find("span", class_="line-clamp-2")
        description = description_tag.get_text(strip=True) if description_tag else ""
        if not description:
            continue

        category_tag = card.find_previous("h5", class_="category-heading")
        category = category_tag.get_text(strip=True) if category_tag else "Outros"

        price_tag = card.find("strong")
        if price_tag is not None:
            price = price_tag.parent.get_text(strip=True).replace("\xa0", " ")
        else:
            price = "Consultar"

        items.append(
            MenuItem(
                dish=dish,
                description=description,
                price=price,
                category=category,
            )
        )

    logger.info("parsed %d dishes from %s", len(items), source)
    return items
