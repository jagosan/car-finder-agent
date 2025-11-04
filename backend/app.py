import sys
print("--- RELOADING app.py ---")
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify, request
import sqlite3
import subprocess
import datetime
import logging
import time
import argparse
import concurrent.futures
from src.scraper.dynamic_scraper import scrape_dynamic_site
from src.database.database import create_connection, create_table, insert_listing, get_all_listings
from src.analysis.gemini_analyzer import analyze_car_data as analyze_with_gemini
from src.analysis.ollama_analyzer import analyze_car_data_ollama as analyze_with_ollama
from src.digest.generator import generate_digest, send_email

import threading

scrape_status = {'status': 'idle', 'message': 'No scrape initiated.'}

app = Flask(__name__)

DATABASE = os.environ.get('DATABASE_PATH', '/home/jmacleod/repos/car-finder-agent/car_finder.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    sql_create_listings_table = """ CREATE TABLE IF NOT EXISTS listings (
                                    id integer PRIMARY KEY,
                                    make text NOT NULL,
                                    model text NOT NULL,
                                    year integer NOT NULL,
                                    price real NOT NULL,
                                    mileage integer,
                                    vin text UNIQUE,
                                    location text,
                                    url text NOT NULL UNIQUE,
                                    source_site text,
                                    scraped_timestamp text NOT NULL
                                ); """

    sql_create_feedback_table = """ CREATE TABLE IF NOT EXISTS feedback (
                                    id integer PRIMARY KEY,
                                    car_id integer NOT NULL,
                                    preference text NOT NULL,
                                    timestamp text NOT NULL,
                                    FOREIGN KEY (car_id) REFERENCES listings (id)
                                ); """
    c.execute(sql_create_listings_table)
    c.execute(sql_create_feedback_table)
    conn.commit()
    conn.close()


@app.route('/')
def hello_world():
    return jsonify(message="Hello from Flask Backend!")

@app.route('/api/cars')
def get_cars():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    
    # Convert Row objects to dictionaries
    cars_list = []
    for car in cars:
        cars_list.append(dict(car))
    
    print(f"Returning {len(cars_list)} cars to the frontend.")
    return jsonify(cars_list)

def analyze_car(car_tuple, model):
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
    car_dict['title'] = f"{car_dict['year']} {car_dict['make']} {car_dict['model']}"
    analysis_input_dict = {
        'title': car_dict['title'],
        'price': f"${car_dict['price']}",
        'mileage': f"{car_dict['mileage']} miles" if car_dict['mileage'] else "N/A",
        'location': car_dict['location'],
        'link': car_dict['link']
    }

    if model == "gemini":
        analysis = analyze_with_gemini(analysis_input_dict)
    else:
        analysis = analyze_with_ollama(analysis_input_dict, model=model)
    
    car_dict['analysis'] = analysis
    return car_dict

@app.route('/api/scrape', methods=['POST'])
def scrape_cars():
    global scrape_status
    if scrape_status['status'] == 'running':
        return jsonify(message="Scraping is already in progress."), 409

    scrape_status = {'status': 'running', 'message': 'Scraping initiated.'}
    threading.Thread(target=_scrape_and_store_data).start()
    return jsonify(message="Scraping initiated successfully! Check /api/scrape-status for updates."), 202

def _scrape_and_store_data():
    global scrape_status
    try:
        logging.basicConfig(level=logging.INFO)
        logging.info("Scrape request received.")

        logging.info("--- 1. Scraping ---")
        try:
            scraped_cars = scrape_dynamic_site()
            logging.info(f"{len(scraped_cars)} cars scraped successfully.")
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}", exc_info=True)
            scraped_cars = []
        
        if not scraped_cars:
            logging.info("No cars scraped. Exiting.")
            scrape_status = {'status': 'completed', 'message': 'No cars scraped.'}
            return

        logging.info("--- 2. Database ---")
        db_file = DATABASE
        conn = create_connection(db_file)
        if conn is None:
            logging.error("Error! cannot create the database connection.")
            scrape_status = {'status': 'failed', 'message': 'Error! cannot create the database connection.'}
            return

        create_table(conn)
        logging.info("Database table created or already exists.")

        for car in scraped_cars:
            try:
                logging.info(f"Processing car: {car}")
                
                make = car.get('make')
                model = car.get('model')
                year = car.get('year')
                price = car.get('price')
                mileage = car.get('mileage')
                vin = car.get('vin')
                location = car.get('location')
                url = car.get('url')
                source_site = "truecar.com"
                scraped_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if all([make, model, year, price, url]):
                    listing_tuple = (
                        make, model, year, price, mileage, vin, location, url, source_site, scraped_timestamp
                    )
                    insert_listing(conn, listing_tuple)
                    logging.info(f"Inserted car into database: {listing_tuple}")
                else:
                    logging.warning(f"Skipping incomplete listing: {car}")

            except (ValueError, IndexError) as e:
                logging.error(f"Error processing car: {car}, Error: {e}", exc_info=True)
                continue

        logging.info("Database processing complete.")
        conn.close()

        logging.info("Scrape request completed successfully.")
        scrape_status = {'status': 'completed', 'message': 'Scraping completed successfully!'}
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}", exc_info=True)
        scrape_status = {'status': 'failed', 'message': f'An unexpected error occurred during scraping: {str(e)}'}

@app.route('/api/scrape-status')
def get_scrape_status():
    global scrape_status
    return jsonify(scrape_status)
    data = request.get_json()
    car_id = data.get('carId')
    preference = data.get('preference')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not car_id or not preference:
        return jsonify(message="Missing carId or preference"), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (car_id, preference, timestamp) VALUES (?, ?, ?)',
            (car_id, preference, timestamp)
        )
        conn.commit()
        conn.close()
        return jsonify(message=f"Feedback for car {car_id} ({preference}) recorded successfully!"), 200
    except sqlite3.Error as e:
        return jsonify(message=f"Failed to record feedback: {e}"), 500

@app.route('/api/test-ollama')
def test_ollama():
    try:
        ollama_api_url = "http://ollama.ollama.svc.cluster.local:11434/api/generate"
        request_data = {
            "model": "mistral",
            "prompt": "Why is the sky blue?",
            "stream": False
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            ollama_api_url,
            data=json.dumps(request_data),
            headers=headers
        )

        return jsonify({
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text
        })
    except Exception as e:
        return jsonify(message="An unexpected error occurred during the test!", error=str(e)), 500

if __name__ == '__main__':
    try:
        init_db()
        app.run(debug=True, host='0.0.0.0', use_reloader=False)
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")