import os
import json
import re
from datetime import datetime, timedelta, time
import pytz
from playwright.sync_api import sync_playwright

# Ustawienia
KEYWORDS = [
    "PONIEDZIAŁEK", "WTOREK", "ŚRODA", "CZWARTEK",
    "PIĄTEK", "SOBOTA", "NIEDZIELA", "NOC"
]
DATE_PATTERN = r"\[(\d{2}\.\d{2}\.\d{4})\]"
FORECAST_FILE = "public/forecast.json"
SHORT_FORECAST_FILE = "public/forecast_ha.json"

# Mapowanie dni
label_map = {
    0: "dzis",
    1: "jutro",
    2: "za_2_dni",
    3: "za_3_dni",
    4: "za_4_dni",
    5: "za_5_dni"
}

def get_first_button_link(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('.elementor-button-link')
        first_button = page.query_selector('.elementor-button-link')
        return first_button.get_attribute('href') if first_button else None

def highlight_temperatures(text):
    pattern = r"(?<!\*)\b(?:ok\.?\s*)?(?:\d{1,2}(?:[-/]\d{1,2})?)°C\b"
    return re.sub(pattern, lambda m: f"**{m.group(0)}**", text)

def clean_forecast(text):
    if "–" in text:
        text = text.split("–", 1)[1].strip()
    text = re.sub(r"\s{2,}", " ", text).strip()
    return highlight_temperatures(text)

def extract_forecasts_by_date(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('.elementor-widget-container')

        paragraphs = page.query_selector_all('.elementor-widget-container p')
        forecasts = {}
        last_date = None

        for p_tag in paragraphs:
            mark = p_tag.query_selector('mark')
            if not mark:
                continue

            mark_text = mark.inner_text().strip().upper()
            if not any(keyword in mark_text for keyword in KEYWORDS):
                continue

            full_text = p_tag.inner_text().strip()
            match = re.search(DATE_PATTERN, mark_text)

            if match:
                date = match.group(1)
                last_date = date
                key = date
            elif "NOC" in mark_text:
                if last_date:
                    key = f"{last_date}N"
                else:
                    today_str = datetime.now().strftime("%d.%m.%Y")
                    key = f"{today_str}N"
                    last_date = today_str
            else:
                continue

            cleaned_text = clean_forecast(full_text)
            forecasts[key] = cleaned_text[0].upper() + cleaned_text[1:]

        return forecasts

def save_to_json(new_data, filename=FORECAST_FILE):
    def sort_key(k):
        return datetime.strptime(k.replace("N", ""), "%d.%m.%Y")

    poland = pytz.timezone("Europe/Warsaw")
    now = datetime.now(poland)
    today = now.date()
    after_21 = now.time() >= time(21, 0)

    # Filtrowanie nowych danych
    filtered_new_data = {}
    for key, value in new_data.items():
        date_str = key.replace("N", "")
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            continue

        if date_obj == today and after_21 and not key.endswith("N"):
            continue  # pomijamy dzisiaj po 21:00 (dzien)
        filtered_new_data[key] = value

    # Wczytaj istniejące dane
    existing_data = {}
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

    # Uzupełnij brakujące dane z forecast.json (z tym samym filtrem)
    for key, value in existing_data.items():
        if key in filtered_new_data:
            continue

        date_str = key.replace("N", "")
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            continue

        if date_obj < today:
            continue
        if date_obj == today and after_21 and not key.endswith("N"):
            continue

        filtered_new_data[key] = value

    # Zapisz scalone dane
    sorted_data = {k: filtered_new_data[k] for k in sorted(filtered_new_data.keys(), key=sort_key)}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=4)

def create_short_forecast(input_file=FORECAST_FILE, output_file=SHORT_FORECAST_FILE):
    with open(input_file, encoding="utf-8") as f:
        forecast_data = json.load(f)

    result = {}
    for delta in range(6):
        day = datetime.now().date() + timedelta(days=delta)
        day_str = day.strftime("%d.%m.%Y")
        base_label = label_map[delta]

        # Dzień
        value_day = forecast_data.get(day_str)
        result[base_label] = value_day if value_day else "Brak danych"

        # Noc
        night_key = day_str + "N"
        value_night = forecast_data.get(night_key)
        result[base_label + "_noc"] = value_night if value_night else "Brak danych"

    full_path = os.path.abspath(output_file)
    print(f"Zapisuję plik forecast do: {full_path}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

# main
main_url = "https://pogodadlaslaska.pl/blog/prognoza-tygodniowa/"
article_url = get_first_button_link(main_url)
if article_url:
    forecast_data = extract_forecasts_by_date(article_url)
    if forecast_data:
        save_to_json(forecast_data)

# ZAWSZE generuj skrócony forecast
create_short_forecast()
