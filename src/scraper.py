"""Web scraping functionality for Pogoda dla Śląska."""
import re
from datetime import datetime
from typing import Optional, Dict

import pytz
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
import time

from config import KEYWORDS, DATE_PATTERN, MAIN_URL, TIMEZONE
from utils import clean_forecast

# Stały User-Agent, aby być traktowanym jak przeglądarka użytkownika
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class PogodaSlaskScraper:
    """Scraper for extracting weather forecasts from pogodadlaslaska.pl."""

    def __init__(self):
        """Initialize the scraper with timezone settings."""
        self.poland = pytz.timezone(TIMEZONE)
        self.today = datetime.now(self.poland).date()

    def get_first_button_link(self, url: str = MAIN_URL) -> Optional[str]:
        """Get the first article button link from the main page."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Używamy context, aby zachować spójność sesji i ustawić User-Agent
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            for attempt in range(5):
                try:
                    # domcontentloaded jest szybsze i bardziej stabilne niż networkidle
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    # Czekamy aż przycisk będzie widoczny
                    page.wait_for_selector(".elementor-button-link", state="visible", timeout=60000)

                    first_button = page.query_selector(".elementor-button-link")
                    link = first_button.get_attribute("href") if first_button else None

                    if link:
                        print(f"Found link after {attempt + 1} attempt(s): {link}")
                        browser.close()
                        return link

                except PlaywrightTimeoutError:
                    page.screenshot(path=f'ferror_attempt_{attempt}.png')
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(5) # Krótka przerwa przed ponowieniem

            browser.close()
            raise Exception("Could not find .elementor-button-link after 5 attempts")

    def _extract_forecast_key(self, mark_text: str, last_date: Optional[str]) -> Optional[str]:
        """Extract forecast key from marked text."""
        match = re.search(DATE_PATTERN, mark_text)
        if match:
            return match.group(1)

        if "NOC" in mark_text:
            return f"{last_date}N" if last_date else f"{self.today.strftime('%d.%m.%Y')}N"
        return None

    def extract_forecasts_by_date(self, url: str) -> Dict[str, str]:
        """Extract forecasts from the article page."""
        forecasts = {}
        last_date = None
        last_key = None

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector('.elementor-widget-container', state="visible")

            paragraphs = page.query_selector_all('.elementor-widget-container p')

            for p_tag in paragraphs:
                mark = p_tag.query_selector('mark')
                if not mark:
                    continue

                mark_text = mark.inner_text().strip().upper()
                full_text = p_tag.inner_text().strip()

                has_keyword = any(keyword in mark_text for keyword in KEYWORDS)

                if has_keyword:
                    key = self._extract_forecast_key(mark_text, last_date)
                    if not key:
                        continue

                    if not key.endswith("N"):
                        last_date = key

                    cleaned_text = clean_forecast(full_text)
                    forecasts[key] = cleaned_text
                    last_key = key
                else:
                    if last_key and "°C" in full_text:
                        cleaned_text = clean_forecast(full_text)
                        if last_key in forecasts:
                            forecasts[last_key] += " " + cleaned_text

            browser.close()

        return forecasts