# Ecowitt Weather Station Data Handler

## Overview
This project provides a complete solution for collecting, storing, and visualizing data from Ecowitt personal weather stations. It includes a backend server for data collection and storage, and a web-based dashboard for real-time monitoring and historical data visualization.

## Features
### Backend
- Real-time weather data collection from Ecowitt weather stations
- Support for multiple weather parameters:
  - Temperature
  - Humidity
  - Barometric pressure
  - Wind speed and direction
  - Rainfall
  - UV index
  - Solar radiation (if supported by your model)
- Data storage in TimescaleDB (time-series database)
- MQTT support for real-time data streaming
- REST API endpoints for data access
- Optional data relay to other systems (e.g., Home Assistant)

### Frontend
- Real-time dashboard showing current conditions
- Interactive historical data charts using Plotly
- 24-hour historical data visualization for:
  - Temperature
  - Humidity
  - Pressure
  - Wind Speed
- Auto-refresh functionality
- Responsive design for mobile devices

## Prerequisites
- Docker and Docker Compose
- Network connectivity
- Ecowitt device configured to send data to your server

## Quick Start

1. Clone the repository

2. Run services in development mode:

```bash
chmod +x init.sh
./init.sh
```
3. Configure your Ecowitt device:
   - In your Ecowitt device settings, set the custom server to:
   - Protocol: HTTP
   - Server IP/Hostname: Your server's IP address
   - Port: 8080
   - Path: /data/report
   - Upload interval: As desired (e.g., 60 seconds)

4. Start the services:

```bash
docker-compose up -d
```

5. Access the dashboard:
   - Frontend Dashboard: http://localhost:5000
   - Backend API: http://localhost:8080


## Configuration

### Backend Configuration
Edit `backend/config.yml` to configure:
- Server settings
- Data relay options
- MQTT settings
- Database connection

### Frontend Configuration
The frontend automatically connects to the backend API. Configuration can be modified in `frontend/app.py`.

## API Endpoints

### Weather Data
- Current conditions: `GET /api/weather/current`
- Historical data: `GET /api/weather/history?start=<ISO_DATE>&end=<ISO_DATE>`
- Data ingestion: `POST /data/report` (used by Ecowitt device)

## Docker Services
- Frontend: Web dashboard (port 5000)
- Backend: Data collection server (port 8080)
- TimescaleDB: Time-series database (port 5432)
- MQTT: Message broker (port 1883)