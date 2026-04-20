from __future__ import annotations

import json
import logging
from pathlib import Path

from ._types import MenuItem
from .bambu import scrape_bambu
from .camaroes import scrape_camaroes

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "json_graphs"


def regenerate_menus() -> None:
    """Re-run both scrapers and overwrite the JSON menus under json_graphs/."""
    _dump(scrape_bambu(DATA_DIR / "bambu.txt"), OUTPUT_DIR / "bambu.json")
    _dump(scrape_camaroes(DATA_DIR / "camaroes.pdf"), OUTPUT_DIR / "camaroes.json")


def _dump(items: list[MenuItem], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = [item.to_json_dict() for item in items]
    destination.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
