"""Configuration and constants for Pogoda dla Śląska scraper."""
import os

# Project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# URLs
MAIN_URL = "https://pogodadlaslaska.pl/blog/prognoza-tygodniowa/"
FORECAST_URL = "https://patrykkotulak.github.io/download-pogoda-slask/forecast.json"

# File paths (relative to project root)
FORECAST_FILE = os.path.join(PROJECT_ROOT, "public", "forecast.json")
SHORT_FORECAST_FILE = os.path.join(PROJECT_ROOT, "public", "forecast_ha.json")

# Scraping keywords
KEYWORDS = [
    "PONIEDZIAŁEK",
    "WTOREK",
    "ŚRODA",
    "CZWARTEK",
    "PIĄTEK",
    "SOBOTA",
    "NIEDZIELA",
    "NOC"
]

# Regex patterns
DATE_PATTERN = r"\[(\d{2}\.\d{2}\.\d{4})\]"
# Temperature pattern handles:
# - Simple: 15°C, -5°C, +10°C
# - Range with slash: 15/20°C, -5/+2°C
# - Range with dash: 15-20°C
# - With "ok.": ok. 15°C, ok. -5/+2°C
# - With "od...do": od -1 do +1°C, od 15 do 20°C
# Uses alternation: first tries "od X do Y°C", then "ok. X°C", then simple "X°C"
TEMPERATURE_PATTERN = r"(?<!\*)(?:\bod\s+[-+]?\d{1,2}\s+do\s+[-+]?\d{1,2}°C|ok\.?\s+[-+]?\d{1,2}(?:[-/][-+]?\d{1,2})?°C|(?<!\w)[-+]?\d{1,2}(?:[-/][-+]?\d{1,2})?°C)(?!\*)"

# Label mapping for short forecast
LABEL_MAP = {
    -1: "wczoraj_noc",
    0: "dzis",
    1: "jutro",
    2: "za_2_dni",
    3: "za_3_dni",
    4: "za_4_dni",
    5: "za_5_dni"
}

# Timezone
TIMEZONE = "Europe/Warsaw"
