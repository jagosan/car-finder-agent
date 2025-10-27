# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install app dependencies
RUN apt-get update && apt-get install -y wget xvfb libxkbcommon-x11-0 x11-xserver-utils xfonts-base
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application's source code
COPY . .

# Set the working directory to the backend
WORKDIR /app/backend

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python3", "app.py"]
