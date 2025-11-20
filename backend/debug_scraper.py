import logging
from src.scraper.dynamic_scraper import scrape_dynamic_site

logging.basicConfig(level=logging.INFO)

def main():
    """
    Tests the dynamic scraper.
    """
    logging.info("[*] Starting dynamic scraper test...")
    scraped_data = scrape_dynamic_site()
    if scraped_data:
        logging.info(f"\n[*] Successfully scraped {len(scraped_data)} listings.")
        for item in scraped_data:
            logging.info(item)
    else:
        logging.info("\n[*] Scraping failed or returned no data.")

if __name__ == "__main__":
    main()