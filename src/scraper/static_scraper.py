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
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        listings = []
        for vehicle_card in soup.find_all('div', class_='vehicle-card-main'):
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

        return listings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == '__main__':
    target_url = "https://www.cars.com/shopping/results/?stock_type=used&makes%5B%5D=honda&models%5B%5D=civic&list_price_max=&maximum_distance=20&zip="
    scraped_data = scrape_static_site(target_url)
    if scraped_data:
        for item in scraped_data:
            print(item)
