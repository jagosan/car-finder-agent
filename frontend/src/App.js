import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scrapeMessage, setScrapeMessage] = useState('');

  const fetchCars = () => {
    fetch('/api/cars')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setCars(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCars();
  }, []);

  const handleScrape = () => {
    setScrapeMessage('Scraping in progress...');
    fetch('/api/scrape', {
      method: 'POST',
    })
      .then(response => response.json())
      .then(data => {
        setScrapeMessage(data.message);
        // Optionally refetch cars after scrape
        fetchCars();
      })
      .catch(error => {
        setScrapeMessage(`Scraping failed: ${error.message}`);
      });
  };

  const handleFeedback = (carId, preference) => {
    fetch('/api/train', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ carId, preference }),
    })
      .then(response => response.json())
      .then(data => {
        console.log(`Feedback for car ${carId}: ${data.message}`);
        // Optionally update UI to show feedback was registered
      })
      .catch(error => {
        console.error(`Failed to send feedback for car ${carId}: ${error.message}`);
      });
  };

  if (loading) {
    return <div className="App">Loading cars...</div>;
  }

  if (error) {
    return <div className="App">Error: {error.message}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Car Listings</h1>
        <button onClick={handleScrape}>Scrape Now</button>
        {scrapeMessage && <p>{scrapeMessage}</p>}
        <div className="car-list">
          {cars.map(car => (
            <div key={car.id} className="car-item">
              <h2>{car.year} {car.make} {car.model}</h2>
              <p>Price: ${car.price}</p>
              <p>Mileage: {car.mileage} miles</p>
              <p>Location: {car.location}</p>
              <p><a href={car.url} target="_blank" rel="noopener noreferrer">View Listing</a></p>
              <div>
                <button onClick={() => handleFeedback(car.id, 'like')}>Like</button>
                <button onClick={() => handleFeedback(car.id, 'dislike')}>Dislike</button>
              </div>
            </div>
          ))}
        </div>
      </header>
    </div>
  );
}

export default App;
