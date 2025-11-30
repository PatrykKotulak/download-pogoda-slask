"""Main entry point for Pogoda dla Śląska scraper."""
from scraper import PogodaSlaskScraper
from processor import ForecastProcessor


def main():
    """
    Main function to scrape, process, and save weather forecasts.

    Process:
    1. Scrape the main page to get the latest article URL
    2. Extract forecasts from the article
    3. Filter and merge with existing data
    4. Save full forecast to JSON
    5. Create and save short forecast for Home Assistant
    """
    print("Starting Pogoda dla Śląska forecast scraper...")

    # Initialize scraper and processor
    scraper = PogodaSlaskScraper()
    processor = ForecastProcessor()

    # Step 1: Get article URL
    print("Fetching latest article URL...")
    article_url = scraper.get_first_button_link()

    if not article_url:
        print("Error: Could not find article URL")
        return

    print(f"Found article: {article_url}")

    # Step 2: Extract forecasts
    print("Extracting forecasts...")
    forecast_data = scraper.extract_forecasts_by_date(article_url)

    if not forecast_data:
        print("Error: No forecast data extracted")
        return

    print(f"Extracted {len(forecast_data)} forecast entries")

    # Step 3: Filter and merge
    print("Filtering and merging with existing data...")
    merged_data = processor.filter_and_merge_forecasts(forecast_data)
    print(f"Final dataset contains {len(merged_data)} entries")

    # Step 4: Save full forecast
    print("Saving full forecast...")
    processor.save_to_json(merged_data)
    print("Full forecast saved successfully")

    # Step 5: Create and save short forecast
    print("Creating short forecast for Home Assistant...")
    processor.save_short_forecast()
    print("Short forecast saved successfully")

    print("\nDone! Forecast data updated.")


if __name__ == "__main__":
    main()
