from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

def scrape_cars_com(driver):
    logging.info("[*] Waiting for car listings to load...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.vehicle-card'))
    )
    logging.info("[*] Car listings found.")

    listings = []
    car_elements = driver.find_elements(By.CSS_SELECTOR, '.vehicle-card')
    logging.info(f"[*] Found {len(car_elements)} car listings.")

    for i, car_element in enumerate(car_elements):
        logging.info(f"  - Processing car {i+1}/{len(car_elements)}...")
        try:
            title_element = car_element.find_element(By.CSS_SELECTOR, '.vehicle-card-title')
            title = title_element.text.strip()
            year, make, *model_parts = title.split()
            model = " ".join(model_parts)

            price_element = car_element.find_element(By.CSS_SELECTOR, '.primary-price')
            price = price_element.text.strip().replace('$', '').replace(',', '')

            mileage_element = car_element.find_element(By.CSS_SELECTOR, 'div.mileage')
            mileage = mileage_element.text.strip().replace(' mi.', '').replace(',', '')

            location_element = car_element.find_element(By.CSS_SELECTOR, 'div.dealer-name')
            location = location_element.text.strip()
            
            url_element = car_element.find_element(By.CSS_SELECTOR, 'a')
            url = url_element.get_attribute('href')


            listings.append({
                'make': make,
                'model': model,
                'year': int(year),
                'price': float(price),
                'mileage': int(mileage),
                'location': location,
                'vin': None,
                'url': url,
            })
            logging.info(f"  - Scraped: {{'make': make, 'model': model, 'year': year, 'price': price}}")
        except Exception as e:
            logging.error(f"Error processing car listing: {e}")
            continue

    return listings

def scrape_dynamic_site(url="file:///app/listings.html"):
    logging.info("[*] Entering scrape_dynamic_site function")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    logging.info("[*] Initializing Chrome driver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        logging.info(f"[*] Navigating to URL: {url}")
        driver.get(url)
        logging.info("[*] Successfully navigated to URL")

        listings = scrape_cars_com(driver)

        logging.info("[*] Scraping completed successfully.")
        return listings

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Save a screenshot for debugging
        driver.save_screenshot("/app/database/screenshot.png")
        logging.info("[*] Screenshot saved to /app/database/screenshot.png")
        return []
    finally:
        logging.info("[*] Closing Chrome driver.")
        driver.quit()

if __name__ == '__main__':
    target_url = "file:///home/jmacleod/repos/car-finder-agent/listings.html"
    print("[*] Starting dynamic scraper...")
    scraped_data = scrape_dynamic_site(target_url)
    if scraped_data:
        print(f"[*] Successfully scraped {len(scraped_data)} listings.")
    else:
        print("[*] Scraping failed or returned no data.")
