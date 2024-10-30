#!/bin/bash

# Stop any existing containers
docker compose down

# Build the new image
docker compose build --no-cache

# Run the container
docker compose up