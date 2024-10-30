# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/recordings

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION_MODE=true
ENV PYTHONPATH=/app

# Run Xvfb and the bot
CMD Xvfb :99 -screen 0 1920x1080x16 & python main.py