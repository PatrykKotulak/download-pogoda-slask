"""Pogoda dla Śląska - Weather forecast scraper."""

__version__ = "1.0.0"
__author__ = "Patryk Kotulak"

from .scraper import PogodaSlaskScraper
from .processor import ForecastProcessor

__all__ = ["PogodaSlaskScraper", "ForecastProcessor"]
