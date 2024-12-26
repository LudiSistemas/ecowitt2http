#!/bin/bash

# Create necessary directories
mkdir -p backend/mqtt/config backend/mqtt/data backend/mqtt/log
mkdir -p nginx/conf.d
chmod -R 777 backend/mqtt

# Copy mosquitto config
cp backend/mqtt/config/mosquitto.conf backend/mqtt/config/

# Generate nginx config
python nginx/generate_config.py

# Create docker network (if it doesn't exist)
docker network create weather_network 2>/dev/null || true

# Load nginx version from config
NGINX_VERSION=$(python -c "import yaml; print(yaml.safe_load(open('nginx/config.yml'))['nginx']['version'])")
NGINX_PORT=$(python -c "import yaml; print(yaml.safe_load(open('nginx/config.yml'))['nginx']['port'])")

# Export variables for docker-compose
export NGINX_VERSION
export NGINX_PORT

# Start services
docker-compose up -d 