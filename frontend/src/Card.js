import React from 'react';
import './Card.css';

const Card = ({ car }) => {
  return (
    <div className="card">
      <img src={car.image_url} alt={`${car.year} ${car.make} ${car.model}`} />
      <div className="card-info">
        <h2>{car.year} {car.make} {car.model}</h2>
        <div className="details">
          <p><strong>Mileage:</strong> {car.mileage}</p>
          <p><strong>Exterior Color:</strong> {car.exterior_color}</p>
          <p><strong>Interior Color:</strong> {car.interior_color}</p>
          <p><strong>Drivetrain:</strong> {car.drivetrain}</p>
          {car.has_accidents ? <p className="has-accidents">Has Accidents</p> : ''}
        </div>
      </div>
    </div>
  );
};

export default Card;
