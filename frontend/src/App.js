import React, { useState, useEffect } from 'react';
import { useSwipeable } from 'react-swipeable';
import Card from './Card';
import './App.css';

function App() {
  const [cars, setCars] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scrapeMessage, setScrapeMessage] = useState('');
  const [scrapeStatus, setScrapeStatus] = useState(null);
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [radius, setRadius] = useState('');

  const fetchCars = () => {
    console.log('Fetching cars...');
    fetch('/api/cars')
      .then(response => {
        console.log('Received response:', response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
          return response.json();
        } else {
          return response.text().then(text => {
            throw new Error(`Unexpected response: ${text}`);
          });
        }
      })
      .then(data => {
        console.log('Received data:', data);
        setCars(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching cars:', error);
        setError(error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCars();
  }, []);

  const handleScrape = (e) => {
    e.preventDefault();
    setScrapeMessage('Scraping in progress...');
    fetch('/api/scrape', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ make, model, year, zip_code: zipCode, radius }),
    })
      .then(response => response.json())
      .then(data => {
        setScrapeMessage(data.message);
        const interval = setInterval(() => {
          fetch('/api/scrape-status')
            .then(response => response.json())
            .then(statusData => {
              setScrapeStatus(statusData);
              if (statusData.status === 'completed' || statusData.status === 'failed') {
                clearInterval(interval);
                fetchCars();
              }
            })
            .catch(error => {
              console.error('Error fetching scrape status:', error);
              clearInterval(interval);
            });
        }, 2000); // Poll every 2 seconds
      })
      .catch(error => {
        setScrapeMessage(`Scraping failed: ${error.message}`);
      });
  };

  const handleFeedback = (carId, preference) => {
    fetch('/api/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ carId, preference }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
          return response.json();
        } else {
          return response.text().then(text => {
            throw new Error(`Unexpected response: ${text}`);
          });
        }
      })
      .then(data => {
        console.log(`Feedback for car ${carId}: ${data.message}`);
        // Optionally update UI to show feedback was registered
      })
      .catch(error => {
        console.error(`Failed to send feedback for car ${carId}: ${error.message}`);
      });
  };

  const [swiping, setSwiping] = useState(false);

  const handlers = useSwipeable({
    onSwiping: () => setSwiping(true),
    onSwiped: () => setSwiping(false),
    onSwipedLeft: () => {
      if (cars.length > 0 && currentIndex < cars.length) {
        handleFeedback(cars[currentIndex].id, 'dislike');
        setCurrentIndex(currentIndex + 1);
      }
    },
    onSwipedRight: () => {
      if (cars.length > 0 && currentIndex < cars.length) {
        handleFeedback(cars[currentIndex].id, 'like');
        setCurrentIndex(currentIndex + 1);
      }
    },
    preventDefaultTouchmoveEvent: true,
    trackMouse: true
  });

  if (loading) {
    return <div className="app">Loading cars...</div>;
  }

  if (error) {
    return <div className="app">Error: {error.message}</div>;
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Car Finder</h1>
        <form onSubmit={handleScrape} className="app__form">
          <input type="text" value={make} onChange={e => setMake(e.target.value)} placeholder="Make" />
          <input type="text" value={model} onChange={e => setModel(e.target.value)} placeholder="Model" />
          <input type="text" value={year} onChange={e => setYear(e.target.value)} placeholder="Year" />
          <input type="text" value={zipCode} onChange={e => setZipCode(e.target.value)} placeholder="Zip Code" />
          <input type="text" value={radius} onChange={e => setRadius(e.target.value)} placeholder="Radius" />
          <button type="submit">Search</button>
        </form>
        {scrapeMessage && <p>{scrapeMessage}</p>}
        {scrapeStatus && <p>Scrape Status: {scrapeStatus.status} - {scrapeStatus.message}</p>}
      </header>
      <div {...handlers} className={`app__cardContainer ${swiping ? 'swiping' : ''}`}>
        {cars.length > 0 && currentIndex < cars.length ? (
          <Card car={cars[currentIndex]} />
        ) : (
          <p>No more cars to show.</p>
        )}
      </div>
    </div>
  );
}

export default App;
