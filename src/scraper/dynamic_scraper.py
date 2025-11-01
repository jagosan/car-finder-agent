from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging

def scrape_dynamic_site(url="https://www.cars.com/shopping/results/?stock_type=used&makes%5B%5D=honda&models%5B%5D=civic&list_price_max=&maximum_distance=20&zip="):
    logging.info("[*] Entering scrape_dynamic_site function")
    """
    Scrapes a dynamic/JS-heavy website to extract car listing data.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        list: A list of dictionaries, where each dictionary represents a car listing.
    """
    # Set up the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no GUI)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    logging.info("[*] Initializing Chrome driver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        logging.info(f"[*] Navigating to URL: {url}")
        driver.get(url)
        logging.info("[*] Successfully navigated to URL")

        # Wait for the main content to load
        logging.info("[*] Waiting for vehicle cards to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vehicle-card-main"))
        )
        logging.info("[*] Vehicle cards found.")

        listings = []
        vehicle_cards = driver.find_elements(By.CLASS_NAME, "vehicle-card-main")
        if not vehicle_cards:
            logging.info("[*] No vehicle cards found. Saving screenshot...")
            driver.save_screenshot("/app/database/screenshot.png")
            logging.info("[*] Screenshot saved to /app/database/screenshot.png")
        logging.info(f"[*] Found {len(vehicle_cards)} vehicle cards.")

        for i, vehicle_card in enumerate(vehicle_cards):
            logging.info(f"  - Processing card {i+1}/{len(vehicle_cards)}...")
            title = vehicle_card.find_element(By.CLASS_NAME, 'title').text.strip()
            price = vehicle_card.find_element(By.CLASS_NAME, 'primary-price').text.strip()
            mileage = vehicle_card.find_element(By.CLASS_NAME, 'mileage').text.strip()
            location = vehicle_card.find_element(By.CLASS_NAME, 'dealer-name').text.strip()
            link = vehicle_card.find_element(By.CLASS_NAME, 'vehicle-card-link').get_attribute('href')
            
            listings.append({
                'title': title,
                'price': price,
                'mileage': mileage,
                'location': location,
                'link': link
            })

        logging.info("[*] Scraping completed successfully.")
        return listings

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
    finally:
        logging.info("[*] Closing Chrome driver.")
        driver.quit()

if __name__ == '__main__':
    # Example usage with a JS-heavy site
    target_url = "https://www.cars.com/shopping/results/?stock_type=used&makes%5B%5D=honda&models%5B%5D=civic&list_price_max=&maximum_distance=20&zip="
    print("[*] Starting dynamic scraper...")
    scraped_data = scrape_dynamic_site(target_url)
    if scraped_data:
        print(f"\n[*] Successfully scraped {len(scraped_data)} listings.")
        # for item in scraped_data:
        #     print(item)
    else:
        print("\n[*] Scraping failed or returned no data.")
