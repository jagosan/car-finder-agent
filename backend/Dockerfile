# Use an official Python runtime as a parent image
FROM python:3.11-slim

LABEL com.example.version="2"

# Set the working directory in the container
WORKDIR /app

# Install app dependencies
RUN apt-get update && apt-get install -y wget xvfb libxkbcommon-x11-0 x11-xserver-utils xfonts-base curl libglib2.0-0 libnss3 libfontconfig1 libxss1
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN apt-get install -y sqlite3

# Copy the application code and dependencies
COPY backend/app.py .
COPY backend/requirements.txt .
COPY src ./src

COPY backend/listings.html .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN ls -l /app
RUN echo $PYTHONPATH

EXPOSE 5000

CMD ["python3", "app.py"]