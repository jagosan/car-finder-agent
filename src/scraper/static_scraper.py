import requests
from bs4 import BeautifulSoup

def scrape_static_site(url):
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
        for article in soup.find_all('article', class_='product_pod'):
            title = article.h3.a['title']
            price = article.find('p', class_='price_color').text
            availability = article.find('p', class_='instock availability').text.strip()
            
            listings.append({
                'title': title,
                'price': price,
                'availability': availability
            })

        return listings

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == '__main__':
    target_url = "http://books.toscrape.com"
    scraped_data = scrape_static_site(target_url)
    if scraped_data:
        for item in scraped_data:
            print(item)
