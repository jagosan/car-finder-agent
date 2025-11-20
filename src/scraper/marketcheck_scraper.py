
import requests
import os

API_KEY = os.environ.get("MARKETCHECK_API_KEY", "YOUR_API_KEY")

def search_cars(api_key, make=None, model=None, year=None, zip_code=None, radius=None):
    """
    Searches for car listings using the Marketcheck API.
    """
    api_url = "https://marketcheck-prod.apigee.net/v2/search/car/active"
    params = {
        "api_key": api_key,
        "make": make,
        "model": model,
        "year": year,
        "zip": zip_code,
        "radius": radius,
        "car_type": "used",
        "start": 0,
        "rows": 50
    }
    
    # Remove any None values from the params dict
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def format_listings(listings_data):
    """
    Formats the listings data from Marketcheck into the format expected by the backend.
    """
    formatted_listings = []
    if "listings" in listings_data:
        for listing in listings_data["listings"]:
            formatted_listing = {
                "make": listing.get("build", {}).get("make"),
                "model": listing.get("build", {}).get("model"),
                "year": listing.get("build", {}).get("year"),
                "price": listing.get("price"),
                "mileage": listing.get("miles"),
                "vin": listing.get("vin"),
                "location": f"{listing.get('dealer', {}).get('city')}, {listing.get('dealer', {}).get('state')}",
                "url": listing.get("vdp_url"),
                "source_site": "marketcheck",
                "scraped_timestamp": listing.get("last_seen_at")
            }
            formatted_listings.append(formatted_listing)
    return formatted_listings

if __name__ == '__main__':
    # Example usage
    if API_KEY == "YOUR_API_KEY":
        print("Please set the MARKETCHECK_API_KEY environment variable.")
    else:
        try:
            # Search for used Toyota Camrys within 50 miles of zip code 90210
            cars_data = search_cars(API_KEY, make="Toyota", model="Camry", zip_code="90210", radius=50)
            formatted_cars = format_listings(cars_data)
            print(f"Found {len(formatted_cars)} cars.")
            # print(formatted_cars)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Marketcheck API: {e}")
