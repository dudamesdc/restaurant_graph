"""Menu scrapers for the two restaurants compared by this project."""

from ._runner import regenerate_menus
from ._types import MenuItem
from .bambu import scrape_bambu
from .camaroes import scrape_camaroes

__all__ = ["MenuItem", "regenerate_menus", "scrape_bambu", "scrape_camaroes"]
