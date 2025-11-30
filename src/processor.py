"""Data processing and filtering for weather forecasts."""
import json
import os
from datetime import datetime, timedelta, time
from typing import Dict

import pytz
import requests

from config import FORECAST_URL, FORECAST_FILE, SHORT_FORECAST_FILE, LABEL_MAP, TIMEZONE


class ForecastProcessor:
    """Processor for filtering, merging, and formatting forecast data."""

    def __init__(self):
        """Initialize the processor with timezone and time-based flags."""
        self.poland = pytz.timezone(TIMEZONE)
        self.now = datetime.now(self.poland)
        self.today = self.now.date()
        self.yesterday = self.today - timedelta(days=1)
        self.after_21 = self.now.time() >= time(21, 0)
        self.before_9 = self.now.time() < time(8, 0)

    def _sort_key(self, key: str) -> datetime:
        """
        Create a sort key from date string.

        Args:
            key: Date string with optional 'N' suffix (e.g., "01.12.2024N")

        Returns:
            datetime object for sorting
        """
        return datetime.strptime(key.replace("N", ""), "%d.%m.%Y")

    def _should_include_forecast(self, key: str, date_obj: datetime.date) -> bool:
        """
        Check if a forecast should be included based on time rules.

        Args:
            key: Forecast key (date with optional 'N')
            date_obj: Parsed date object

        Returns:
            True if forecast should be included
        """
        # Skip old forecasts (except yesterday night before 9:00)
        if date_obj < self.today:
            return key.endswith("N") and date_obj == self.yesterday and self.before_9

        # Yesterday night only before 9:00
        if key.endswith("N") and date_obj == self.yesterday:
            return self.before_9

        # Skip today after 21:00 (except night forecasts)
        if date_obj == self.today and self.after_21 and not key.endswith("N"):
            return False

        return True

    def filter_and_merge_forecasts(self, new_data: Dict[str, str]) -> Dict[str, str]:
        """
        Filter new data and merge with existing data from GitHub Pages.

        Args:
            new_data: Newly scraped forecast data

        Returns:
            Filtered and merged forecast dictionary
        """
        filtered_new_data = {}

        # Filter new data
        for key, value in new_data.items():
            date_str = key.replace("N", "")
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            except ValueError:
                continue

            if self._should_include_forecast(key, date_obj):
                filtered_new_data[key] = value

        # Fetch existing data from GitHub Pages
        existing_data = self._fetch_existing_data()

        # Merge with existing data
        for key, value in existing_data.items():
            if key in filtered_new_data:
                continue

            date_str = key.replace("N", "")
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            except ValueError:
                continue

            if self._should_include_forecast(key, date_obj):
                filtered_new_data[key] = value

        # Sort by date
        return {k: filtered_new_data[k] for k in sorted(filtered_new_data.keys(), key=self._sort_key)}

    def _fetch_existing_data(self) -> Dict[str, str]:
        """
        Fetch existing forecast data from GitHub Pages.

        Returns:
            Dictionary of existing forecasts, empty dict on error
        """
        try:
            response = requests.get(FORECAST_URL, timeout=10)
            if response.ok:
                return response.json()
        except Exception:
            pass
        return {}

    def create_short_forecast(self, forecast_data: Dict[str, str]) -> Dict[str, str]:
        """
        Create short forecast in Home Assistant compatible format.

        Args:
            forecast_data: Full forecast data with date keys

        Returns:
            Dictionary with label keys (dzis, jutro, etc.)
        """
        result = {}

        for delta, base_label in LABEL_MAP.items():
            if delta == -1:
                # Yesterday night (only before 9:00)
                night_key_yesterday = self.yesterday.strftime("%d.%m.%Y") + "N"
                result[base_label] = (
                    forecast_data.get(night_key_yesterday, "Brak danych")
                    if self.before_9
                    else "Brak danych"
                )
            else:
                # Day and night forecasts
                day = self.today + timedelta(days=delta)
                day_str = day.strftime("%d.%m.%Y")
                result[base_label] = forecast_data.get(day_str, "Brak danych")
                result[base_label + "_noc"] = forecast_data.get(day_str + "N", "Brak danych")

        return result

    def save_to_json(self, data: Dict[str, str], filename: str = FORECAST_FILE) -> None:
        """
        Save forecast data to JSON file.

        Args:
            data: Forecast data to save
            filename: Output file path
        """
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_short_forecast(self, input_file: str = FORECAST_FILE, output_file: str = SHORT_FORECAST_FILE) -> None:
        """
        Create and save short forecast from full forecast file.

        Args:
            input_file: Input forecast file path
            output_file: Output short forecast file path
        """
        with open(input_file, encoding="utf-8") as f:
            forecast_data = json.load(f)

        short_forecast = self.create_short_forecast(forecast_data)

        full_path = os.path.abspath(output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(short_forecast, f, ensure_ascii=False, indent=4)

        print(f"Short forecast saved to: {full_path}")
