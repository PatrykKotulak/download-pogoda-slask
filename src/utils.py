"""Utility functions for text processing."""
import re
from config import TEMPERATURE_PATTERN


def highlight_temperatures(text: str) -> str:
    """
    Highlight temperatures in the text by wrapping them in markdown bold.

    Args:
        text: Input text containing temperatures

    Returns:
        Text with temperatures wrapped in **...**
    """
    return re.sub(TEMPERATURE_PATTERN, lambda m: f"**{m.group(0)}**", text)


def clean_forecast(text: str) -> str:
    """
    Clean forecast text by removing day prefix and extra whitespace.

    Args:
        text: Raw forecast text from webpage

    Returns:
        Cleaned and formatted forecast text
    """
    # Remove day prefix (e.g., "PONIEDZIAŁEK – ")
    if "–" in text:
        text = text.split("–", 1)[1].strip()

    # Replace multiple spaces with single space
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Highlight temperatures
    text = highlight_temperatures(text)

    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    return text
