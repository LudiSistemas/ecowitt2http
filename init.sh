#!/bin/bash

# Create necessary directories
mkdir -p backend/mqtt/config backend/mqtt/data backend/mqtt/log
chmod -R 777 backend/mqtt

# Copy mosquitto config
cp backend/mqtt/config/mosquitto.conf backend/mqtt/config/

# Create docker network (if it doesn't exist)
docker network create weather_network 2>/dev/null || true

# Start services
docker-compose up -d 