import requests
import json
import sys
print("--- RELOADING app.py ---")
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify, request
import sqlite3
import datetime
import logging
import yaml # Import PyYAML
from src.analysis.gemini_analyzer import analyze_car_data as analyze_with_gemini
from src.analysis.ollama_analyzer import analyze_car_data_ollama as analyze_with_ollama
from src.digest.generator import generate_digest, send_email
from backend.db import get_db_connection, init_db

from kubernetes import client, config

scrape_status = {'status': 'idle', 'message': 'No scrape initiated.'}

app = Flask(__name__)

# Load Kubernetes configuration
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config() # Fallback for local development

batch_v1 = client.BatchV1Api()

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

@app.route('/api/listings', methods=['POST'])
def add_listings():
    listings = request.get_json()
    if not listings:
        return jsonify(message="No listings provided"), 400

    conn = get_db_connection()
    c = conn.cursor()
    new_cars_count = 0
    for car in listings:
        try:
            c.execute(
                """
                INSERT INTO listings (make, model, year, price, mileage, vin, location, url, source_site, scraped_timestamp, image_url, exterior_color, interior_color, drivetrain, has_accidents)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    car.get('make'), car.get('model'), car.get('year'), car.get('price'),
                    car.get('mileage'), car.get('vin'), car.get('location'), car.get('url'),
                    car.get('source_site'), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    car.get('image_url'), car.get('exterior_color'), car.get('interior_color'),
                    car.get('drivetrain'), car.get('has_accidents')
                )
            )
            new_cars_count += 1
        except sqlite3.IntegrityError:
            # This will happen if the URL or VIN is not unique, which is expected.
            pass
    conn.commit()
    conn.close()
    return jsonify(message=f"Added {new_cars_count} new car listings."), 201

@app.route('/api/scrape', methods=['POST'])
def scrape_cars():
    global scrape_status
    if scrape_status['status'] == 'running':
        return jsonify(message="Scraping is already in progress."), 409

    scrape_status = {'status': 'running', 'message': 'Scraping initiated.'}
    
    try:
        # Get search criteria from the request
        search_criteria = request.get_json()
        if not search_criteria:
            search_criteria = {}

        # Load the job manifest
        with open("kubernetes/scraper-job.yaml", "r") as f:
            job_manifest = yaml.safe_load(f)

        # Generate a unique job name
        job_name = f"car-scraper-job-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        job_manifest['metadata']['name'] = job_name
        job_manifest['metadata']['labels'] = {'app': 'car-finder', 'job-type': 'scraper'} # Add labels for status tracking

        # Pass search criteria as arguments to the job
        args = []
        for key, value in search_criteria.items():
            if value:
                args.append(f"--{key}={value}")
        
        job_manifest['spec']['template']['spec']['containers'][0]['args'] = args

        # Create the job
        batch_v1.create_namespaced_job(body=job_manifest, namespace="default") # Assuming 'default' namespace
        scrape_status = {'status': 'job_created', 'message': f'Scraping job {job_name} created successfully!'}
        return jsonify(message=f"Scraping job {job_name} created successfully! Check /api/scrape-status for updates."), 202
    except client.ApiException as e:
        logging.error(f"Error creating Kubernetes Job: {e}")
        scrape_status = {'status': 'failed', 'message': f'Error creating Kubernetes Job: {str(e)}'}
        return jsonify(message=f"Error creating Kubernetes Job: {str(e)}"), 500
    except FileNotFoundError:
        logging.error("kubernetes/scraper-job.yaml not found.")
        scrape_status = {'status': 'failed', 'message': 'Scraper job manifest not found.'}
        return jsonify(message='Scraper job manifest not found.'), 500
    except yaml.YAMLError as e:
        logging.error(f"Error parsing kubernetes/scraper-job.yaml: {e}")
        scrape_status = {'status': 'failed', 'message': f'Error parsing scraper job manifest: {str(e)}'}
        return jsonify(message=f'Error parsing scraper job manifest: {str(e)}'), 500

@app.route('/api/scrape-status')
def get_scrape_status():
    global scrape_status
    
    try:
        # List jobs with the 'job-type: scraper' label
        jobs = batch_v1.list_namespaced_job(namespace="default", label_selector="job-type=scraper")
        
        latest_job = None
        latest_creation_time = None

        for job in jobs.items:
            if job.metadata.creation_timestamp:
                if latest_creation_time is None or job.metadata.creation_timestamp > latest_creation_time:
                    latest_creation_time = job.metadata.creation_timestamp
                    latest_job = job
        
        if latest_job:
            if latest_job.status.succeeded:
                scrape_status = {'status': 'completed', 'message': f"Job {latest_job.metadata.name} succeeded."}
            elif latest_job.status.failed:
                scrape_status = {'status': 'failed', 'message': f"Job {latest_job.metadata.name} failed. Reason: {latest_job.status.conditions[0].reason if latest_job.status.conditions else 'Unknown'}"}
            elif latest_job.status.active:
                scrape_status = {'status': 'running', 'message': f"Job {latest_job.metadata.name} is running."}
            else:
                scrape_status = {'status': 'unknown', 'message': f"Job {latest_job.metadata.name} status unknown."}
        else:
            scrape_status = {'status': 'idle', 'message': 'No scraper jobs found.'}

    except client.ApiException as e:
        logging.error(f"Error getting Kubernetes Job status: {e}")
        scrape_status = {'status': 'failed', 'message': f'Error getting Kubernetes Job status: {str(e)}'}
    

    return jsonify(scrape_status)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
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
        # Assuming `requests` is imported, if not add it.
        import requests
        import json
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

@app.route('/api/init-db')
def init_db_route():
    import io
    import sys
    from backend.db import init_db

    # Redirect stdout to a string buffer
    old_stdout = sys.stdout
    sys.stdout = new_stdout = io.StringIO()

    init_db()

    # Restore stdout
    sys.stdout = old_stdout

    return new_stdout.getvalue()

if __name__ == '__main__':
    try:
        init_db()
        app.run(debug=True, host='0.0.0.0', use_reloader=False)
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")
