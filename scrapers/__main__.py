"""Regenerate the JSON menus under json_graphs/. Invoked as `python -m scrapers`."""

import logging

from . import regenerate_menus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
regenerate_menus()
