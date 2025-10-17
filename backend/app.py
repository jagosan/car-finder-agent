from flask import Flask, jsonify, request
import sqlite3
import subprocess
import datetime

app = Flask(__name__)

DATABASE = '/app/database/car_finder.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

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
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify(message="Scraping initiated successfully!", output=result.stdout), 200
    except subprocess.CalledProcessError as e:
        return jsonify(message="Scraping failed!", error=e.stderr), 500

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
    app.run(debug=True, host='0.0.0.0')
