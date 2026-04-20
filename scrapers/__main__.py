"""Regenerate the JSON menus under json_graphs/ by running both scrapers."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from . import MenuItem, scrape_bambu, scrape_camaroes

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "json_graphs"


def _dump(items: list[MenuItem], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = [item.to_json_dict() for item in items]
    destination.write_text(
        json.dumps(payload, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    _dump(scrape_bambu(DATA_DIR / "bambu.txt"), OUTPUT_DIR / "bambu.json")
    _dump(scrape_camaroes(DATA_DIR / "camaroes.pdf"), OUTPUT_DIR / "camaroes.json")


if __name__ == "__main__":
    main()
