"""Web scraping functionality for Pogoda dla Śląska."""
import re
from datetime import datetime
from typing import Optional, Dict

import pytz
from playwright.sync_api import sync_playwright, Page

from config import KEYWORDS, DATE_PATTERN, MAIN_URL, TIMEZONE
from utils import clean_forecast


class PogodaSlaskScraper:
    """Scraper for extracting weather forecasts from pogodadlaslaska.pl."""

    def __init__(self):
        """Initialize the scraper with timezone settings."""
        self.poland = pytz.timezone(TIMEZONE)
        self.today = datetime.now(self.poland).date()

    def get_first_button_link(self, url: str = MAIN_URL) -> Optional[str]:
        """
        Get the first article button link from the main page.

        Args:
            url: URL of the main page (default: MAIN_URL from config)

        Returns:
            URL of the first article or None if not found
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('.elementor-button-link')
            first_button = page.query_selector('.elementor-button-link')
            link = first_button.get_attribute('href') if first_button else None
            browser.close()
            return link

    def _extract_forecast_key(self, mark_text: str, last_date: Optional[str]) -> Optional[str]:
        """
        Extract forecast key from marked text.

        Args:
            mark_text: Text from the <mark> tag
            last_date: Last extracted date (for night forecasts)

        Returns:
            Forecast key (e.g., "01.12.2024" or "01.12.2024N") or None
        """
        # Check for date pattern
        match = re.search(DATE_PATTERN, mark_text)
        if match:
            return match.group(1)

        # Check for night forecast
        if "NOC" in mark_text:
            if last_date:
                return f"{last_date}N"
            else:
                today_str = self.today.strftime("%d.%m.%Y")
                return f"{today_str}N"

        return None

    def extract_forecasts_by_date(self, url: str) -> Dict[str, str]:
        """
        Extract forecasts from the article page.

        This method handles multiple paragraph formats:
        1. Standard paragraphs with day/date keywords (creates new entry)
        2. Additional paragraphs with temperature (appended to previous entry)

        Args:
            url: URL of the article page

        Returns:
            Dictionary with date keys and forecast text values
        """
        forecasts = {}
        last_date = None
        last_key = None

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('.elementor-widget-container')

            paragraphs = page.query_selector_all('.elementor-widget-container p')

            for p_tag in paragraphs:
                mark = p_tag.query_selector('mark')
                if not mark:
                    continue

                mark_text = mark.inner_text().strip().upper()
                full_text = p_tag.inner_text().strip()

                # Check if this is a forecast paragraph with keyword
                has_keyword = any(keyword in mark_text for keyword in KEYWORDS)

                if has_keyword:
                    # Extract the forecast key
                    key = self._extract_forecast_key(mark_text, last_date)
                    if not key:
                        continue

                    # Update last_date if this is a date (not a night forecast)
                    if not key.endswith("N"):
                        last_date = key

                    # Extract and clean the full text
                    cleaned_text = clean_forecast(full_text)
                    forecasts[key] = cleaned_text
                    last_key = key
                else:
                    # No keyword, but check if it contains temperature
                    # If yes, append to last key
                    if last_key and "°C" in full_text:
                        # This is an additional section with temperature
                        # Append to the previous forecast
                        cleaned_text = clean_forecast(full_text)
                        if last_key in forecasts:
                            forecasts[last_key] += " " + cleaned_text

            browser.close()

        return forecasts
