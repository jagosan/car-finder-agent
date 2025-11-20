import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backend import app

@pytest.fixture
def init_database():
    if os.path.exists(app.DATABASE):
        os.remove(app.DATABASE)
    app.init_db()
    yield
    if os.path.exists(app.DATABASE):
        os.remove(app.DATABASE)

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

from unittest.mock import patch

def test_hello_world(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.get_json() == {'message': 'Hello from Flask Backend!'}

@patch('backend.app.scrape_dynamic_site')
def test_scrape_cars(mock_scrape_dynamic_site, client, init_database):
    # Mock the scraper to return some dummy data
    mock_scrape_dynamic_site.return_value = [
        {'title': '2022 Honda Civic', 'price': '$25,000', 'mileage': '15,000 miles', 'location': 'Los Angeles, CA', 'link': 'http://example.com/car3'}
    ]

    rv = client.post('/scrape?model=mistral')
    assert rv.status_code == 200
    assert rv.get_json() == {'message': 'Scraping initiated successfully!'}

    # Check that the data was inserted into the database
    with app.app.app_context():
        conn = app.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM listings WHERE make = 'Honda' AND model = 'Civic'")
        car = c.fetchone()
        conn.close()
    assert car is not None
    assert car['year'] == 2022

def test_train_model(client, init_database):
    # Create a car to provide feedback on
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO listings (make, model, year, price, url, source_site, scraped_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
              ('Honda', 'Accord', 2023, 30000, 'http://example.com/car4', 'example.com', '2025-10-26 12:00:00'))
    conn.commit()
    car_id = c.lastrowid
    conn.close()

    # Provide feedback
    rv = client.post('/train', json={'carId': car_id, 'preference': 'like'})
    assert rv.status_code == 200
    assert rv.get_json() == {f'message': f'Feedback for car {car_id} (like) recorded successfully!'}

    # Check that the feedback was stored in the database
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM feedback WHERE car_id = ?", (car_id,))
    feedback = c.fetchone()
    assert feedback is not None
    assert feedback['preference'] == 'like'

def test_get_cars(client, init_database):
    # Create some dummy data
    conn = app.get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO listings (make, model, year, price, url, source_site, scraped_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
              ('Honda', 'Civic', 2022, 25000, 'http://example.com/car2', 'example.com', '2025-10-26 12:00:00'))
    conn.commit()
    conn.close()

    rv = client.get('/cars')
    assert rv.status_code == 200
    assert len(rv.get_json()) == 1
    assert rv.get_json()[0]['make'] == 'Honda'
