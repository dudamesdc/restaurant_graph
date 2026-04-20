"""Menu scrapers for the two restaurants compared by this project."""

from ._types import MenuItem
from .bambu import scrape_bambu
from .camaroes import scrape_camaroes

__all__ = ["MenuItem", "scrape_bambu", "scrape_camaroes"]
