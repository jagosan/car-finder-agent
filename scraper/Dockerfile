# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code and dependencies
COPY scraper/requirements.txt .
COPY src ./src
COPY scraper ./scraper

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the python path
ENV PYTHONPATH /app

# Command to run the scraper
CMD ["python3", "scraper/scrape.py"]