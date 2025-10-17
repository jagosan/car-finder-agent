import argparse
import datetime
from src.scraper.dynamic_scraper import scrape_dynamic_site
from src.database.database import create_connection, create_table, insert_listing, get_all_listings
from src.analysis.gemini_analyzer import analyze_car_data as analyze_with_gemini
from src.analysis.ollama_analyzer import analyze_car_data_ollama as analyze_with_ollama
from src.digest.generator import generate_digest, send_email


def main():
    parser = argparse.ArgumentParser(description="AI Car Finder Agent")
    parser.add_argument(
        "--model",
        default="gemini",
        help="The analysis model to use.",
    )
    parser.add_argument(
        "--recipient",
        type=str,
        default="test@example.com",
        help="The email address to send the digest to.",
    )
    args = parser.parse_args()

    # --- 1. Scraping ---
    scraped_cars = scrape_dynamic_site()
    if not scraped_cars:
        print("No cars scraped. Exiting.")
        return

    # --- 2. Database ---
    db_file = "car_finder.db"
    conn = create_connection(db_file)
    if conn is None:
        print("Error! cannot create the database connection.")
        return

    create_table(conn)

    for car in scraped_cars:
        # Basic data parsing and cleaning
        try:
            title_parts = car.get('title', '').split()
            year = int(title_parts[0]) if title_parts and title_parts[0].isdigit() else None
            make = title_parts[1] if len(title_parts) > 1 else None
            model = " ".join(title_parts[2:]) if len(title_parts) > 2 else None

            price_str = car.get('price', '').replace('$', '').replace(',', '').strip()
            price = float(price_str) if price_str else None

            mileage_str = car.get('mileage', '').replace('miles', '').replace(',', '').strip()
            mileage = int(mileage_str) if mileage_str.isdigit() else None
            
            vin = car.get('vin', None) # VIN is not scraped yet
            location = car.get('location', None)
            url = car.get('link', None)
            source_site = "cars.com" # Hardcoded for now
            scraped_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if all([year, make, model, price, url]):
                listing_tuple = (
                    make, model, year, price, mileage, vin, location, url, source_site, scraped_timestamp
                )
                insert_listing(conn, listing_tuple)
            else:
                print(f"Skipping incomplete listing: {car.get('title')}")

        except (ValueError, IndexError) as e:
            print(f"Error processing car: {car.get('title')}, Error: {e}")
            continue

    # --- 3. Analysis ---
    all_cars_tuples = get_all_listings(conn)
    conn.close() # Close connection after fetching data

    analyzed_cars = []
    for car_tuple in all_cars_tuples:
        # Convert tuple to dictionary for analysis
        car_dict = {
            'id': car_tuple[0],
            'make': car_tuple[1],
            'model': car_tuple[2],
            'year': car_tuple[3],
            'price': car_tuple[4],
            'mileage': car_tuple[5],
            'vin': car_tuple[6],
            'location': car_tuple[7],
            'link': car_tuple[8],
            'source_site': car_tuple[9],
            'scraped_timestamp': car_tuple[10]
        }
        # The analysis function expects a different dict structure
        analysis_input_dict = {
            'title': f"{car_dict['year']} {car_dict['make']} {car_dict['model']}",
            'price': f"${car_dict['price']}",
            'mileage': f"{car_dict['mileage']} miles" if car_dict['mileage'] else "N/A",
            'location': car_dict['location'],
            'link': car_dict['link']
        }

        if args.model == "gemini":
            analysis = analyze_with_gemini(analysis_input_dict)
        else:
            analysis = analyze_with_ollama(analysis_input_dict, model=args.model)
        
        car_dict['analysis'] = analysis
        analyzed_cars.append(car_dict)

    # --- 4. Digest Generation ---
    if analyzed_cars:
        html_digest = generate_digest(analyzed_cars)
        send_email(html_digest, args.recipient)
    else:
        print("No cars to analyze and generate digest.")


if __name__ == "__main__":
    main()