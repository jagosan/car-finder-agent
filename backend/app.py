from flask import Flask, jsonify, request
import sqlite3
import subprocess
import datetime

import logging

app = Flask(__name__)

DATABASE = '/app/database/car_finder.db'

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

@app.route('/cars')
def get_cars():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    
    # Convert Row objects to dictionaries
    cars_list = []
    for car in cars:
        cars_list.append(dict(car))
    
    return jsonify(cars_list)

@app.route('/scrape', methods=['POST'])
def scrape_cars():
    try:
        # Run the main.py script as a subprocess
        # Assuming main.py is in the parent directory
        result = subprocess.run(
            ["python3", "../main.py", "--model", "mistral"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300 # 5 minutes timeout
        )

        if result.returncode != 0:
            logging.error(f"Scraping script failed with exit code {result.returncode}")
            logging.error(f"Stdout: {result.stdout}")
            logging.error(f"Stderr: {result.stderr}")
            return jsonify(message="Scraping failed!", error=result.stderr), 500

        return jsonify(message="Scraping initiated successfully!", output=result.stdout), 200
    except subprocess.TimeoutExpired as e:
        logging.error(f"Scraping script timed out after {e.timeout} seconds.")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return jsonify(message="Scraping timed out!", error=f"Scraping timed out after {e.timeout} seconds."), 500
    except Exception as e:
        logging.error(str(e))
        return jsonify(message="An unexpected error occurred during scraping!", error=str(e)), 500

@app.route('/train', methods=['POST'])
def train_model():
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

if __name__ == '__main__':
    try:
        init_db()
        app.run(debug=True, host='0.0.0.0')
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")
