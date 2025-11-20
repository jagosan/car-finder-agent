
import argparse
import requests
import json
import os
from src.scraper.marketcheck_scraper import search_cars, format_listings

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Marketcheck car scraper.')
    parser.add_argument('--make', type=str, help='The make of the car to search for.')
    parser.add_argument('--model', type=str, help='The model of the car to search for.')
    parser.add_argument('--year', type=str, help='The year of the car to search for.')
    parser.add_argument('--zip_code', type=str, help='The zip code to search around.')
    parser.add_argument('--radius', type=str, help='The radius to search in.')
    parser.add_argument('--api_url', type=str, default='http://backend-service:5000/api/listings',
                        help='The URL of the backend API to post the scraped data.')
    args = parser.parse_args()

    api_key = os.environ.get("MARKETCHECK_API_KEY")
    if not api_key:
        print("Please set the MARKETCHECK_API_KEY environment variable.")
    else:
        print("[*] Starting Marketcheck scraper...")
        try:
            scraped_data = search_cars(api_key, args.make, args.model, args.year, args.zip_code, args.radius)
            formatted_data = format_listings(scraped_data)
            if formatted_data:
                print(f"[*] Successfully scraped {len(formatted_data)} listings.")
                try:
                    response = requests.post(args.api_url, json=formatted_data, headers={'Content-Type': 'application/json'})
                    response.raise_for_status()
                    print(f"[*] Successfully sent scraped data to the backend: {response.json().get('message')}")
                except requests.exceptions.RequestException as e:
                    print(f"[!] Error sending scraped data to the backend: {e}")
            else:
                print("[*] Scraping failed or returned no data.")
        except requests.exceptions.RequestException as e:
            print(f"[!] Error calling Marketcheck API: {e}")
