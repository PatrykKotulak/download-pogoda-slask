# Pogoda dla Śląska - Scraper

Automatyczny scraper prognoz pogody z serwisu [Pogoda dla Śląska](https://pogodadlaslaska.pl/).

## Opis

Ten projekt automatycznie pobiera tygodniowe prognozy pogody ze strony Pogoda dla Śląska i zapisuje je w formacie JSON. Generuje dwa pliki:

- `public/forecast.json` - Pełna prognoza z datami
- `public/forecast_ha.json` - Prognoza w formacie dla Home Assistant

## Struktura projektu

```
.
├── src/
│   ├── __init__.py       # Inicjalizacja pakietu
│   ├── config.py         # Konfiguracja i stałe
│   ├── main.py           # Punkt wejścia programu
│   ├── processor.py      # Przetwarzanie i filtrowanie danych
│   ├── scraper.py        # Logika scrapowania web
│   └── utils.py          # Funkcje pomocnicze
├── public/               # Wygenerowane pliki JSON
├── .github/workflows/    # GitHub Actions
├── requirements.txt      # Zależności Python
└── README.md            # Dokumentacja
```

## Wymagania

- Python 3.11+
- Playwright
- pytz
- requests

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/patrykkotulak/download-pogoda-slask.git
cd download-pogoda-slask
```

2. Utwórz wirtualne środowisko:
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
# lub
source .venv/bin/activate      # Linux/Mac
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Użycie

Uruchom scraper:

```bash
python src/main.py
```

Program wykona następujące kroki:
1. Pobierze URL najnowszej prognozy z głównej strony
2. Wydobędzie prognozy z artykułu
3. Scali dane z istniejącymi prognozami z GitHub Pages
4. Zapisze pełną prognozę do `public/forecast.json`
5. Utworzy skróconą prognozę dla Home Assistant w `public/forecast_ha.json`

## Automatyzacja

Projekt wykorzystuje GitHub Actions do automatycznego aktualizowania prognoz 4 razy dziennie:

- **03:00** - Poranna aktualizacja
- **09:00** - Przedpołudniowa aktualizacja
- **21:00** - Wieczorna aktualizacja
- **22:30** - Nocna aktualizacja

Wygenerowane pliki JSON są publikowane na GitHub Pages: https://patrykkotulak.github.io/download-pogoda-slask/

## Format danych

### forecast.json
```json
{
  "30.11.2024": "Zachmurzenie zmienne...",
  "30.11.2024N": "Noc: Zachmurzenie duże...",
  "01.12.2024": "...",
  ...
}
```

### forecast_ha.json (dla Home Assistant)
```json
{
  "wczoraj_noc": "Brak danych",
  "dzis": "Zachmurzenie zmienne...",
  "dzis_noc": "...",
  "jutro": "...",
  "jutro_noc": "...",
  "za_2_dni": "...",
  "za_2_dni_noc": "...",
  "za_3_dni": "...",
  "za_3_dni_noc": "...",
  "za_4_dni": "...",
  "za_4_dni_noc": "...",
  "za_5_dni": "...",
  "za_5_dni_noc": "..."
}
```

## Architektura

### config.py
Zawiera wszystkie stałe i konfigurację:
- URL-e źródłowe
- Ścieżki do plików
- Wzorce regex
- Mapowanie etykiet

### scraper.py
Klasa `PogodaSlaskScraper` odpowiedzialna za:
- Pobieranie linku do najnowszej prognozy
- Wydobywanie treści prognoz ze strony
- Parsowanie dat i tekstów

### processor.py
Klasa `ForecastProcessor` odpowiedzialna za:
- Filtrowanie prognoz według czasu (przed 9:00, po 21:00)
- Scalanie z istniejącymi danymi
- Tworzenie wersji skróconej dla HA
- Zapisywanie do plików JSON

### utils.py
Funkcje pomocnicze:
- Formatowanie temperatury (oznaczanie bold)
- Czyszczenie tekstu prognozy

### main.py
Punkt wejścia łączący wszystkie komponenty.

## Logika czasowa

Program stosuje specjalne reguły czasowe:

- **Przed 9:00** - Pokazuje "wczoraj_noc"
- **Po 21:00** - Pomija dzisiejszą prognozę dzienną (pokazuje tylko noc)
- Stara się uzupełnić brakujące dane z GitHub Pages

## Rozwój

Aby uruchomić w trybie deweloperskim:

```bash
# Aktywuj środowisko wirtualne
source .venv/Scripts/activate

# Uruchom scraper
python src/main.py
```

## Troubleshooting

### Błędy Playwright
Jeśli widzisz błędy związane z Playwright:
```bash
playwright install chromium
playwright install-deps chromium
```

### Brak katalogu public
Program automatycznie tworzy katalog `public/` jeśli nie istnieje.

### Timeout podczas scrapowania
Sprawdź czy strona https://pogodadlaslaska.pl jest dostępna.

## Licencja

MIT

## Autor

Patryk Kotulak ([@patrykkotulak](https://github.com/patrykkotulak))

## Linki

- [Pogoda dla Śląska](https://pogodadlaslaska.pl/)
- [GitHub Pages (JSON)](https://patrykkotulak.github.io/download-pogoda-slask/)
- [Issues](https://github.com/patrykkotulak/download-pogoda-slask/issues)
