import requests
from bs4 import BeautifulSoup

def scrape_static_site(url="https://www.cars.com/shopping/results/?stock_type=used&makes%5B%5D=honda&models%5B%5D=civic&list_price_max=&maximum_distance=20&zip="):
    """
    Scrapes a static website to extract car listing data.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        list: A list of dictionaries, where each dictionary represents a car listing.
    """
    try:
        print(f"[*] Scraping started for URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        print(f"[*] Request finished with status code: {response.status_code}")
        response.raise_for_status()  # Raise an exception for bad status codes

        print("[*] Parsing HTML content with BeautifulSoup...")
        soup = BeautifulSoup(response.content, 'html.parser')

        listings = []
        vehicle_cards = soup.find_all('div', class_='vehicle-card-main')
        print(f"[*] Found {len(vehicle_cards)} vehicle cards.")

        for i, vehicle_card in enumerate(vehicle_cards):
            print(f"  - Processing card {i+1}/{len(vehicle_cards)}...")
            title = vehicle_card.find('h2', class_='title').text.strip()
            price = vehicle_card.find('span', class_='primary-price').text.strip()
            mileage = vehicle_card.find('div', class_='mileage').text.strip()
            location = vehicle_card.find('div', class_='dealer-name').text.strip()
            link = "https://www.cars.com" + vehicle_card.find('a', class_='vehicle-card-link')['href']
            
            listings.append({
                'title': title,
                'price': price,
                'mileage': mileage,
                'location': location,
                'link': link
            })
        
        print("[*] Scraping completed successfully.")
        return listings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == '__main__':
    target_url = "https://www.cars.com/shopping/results/?stock_type=used&makes%5B%5D=honda&models%5B%5D=civic&list_price_max=&maximum_distance=20&zip="
    print("[*] Starting static scraper...")
    scraped_data = scrape_static_site(target_url)
    if scraped_data:
        print(f"\n[*] Successfully scraped {len(scraped_data)} listings.")
        # for item in scraped_data:
        #     print(item)
    else:
        print("\n[*] Scraping failed or returned no data.")
