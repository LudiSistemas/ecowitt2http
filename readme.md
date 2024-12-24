
 # Ecowitt Weather Station Data Handler

## Overview
This project provides tools to collect, process, and display data from Ecowitt personal weather stations. It enables users to monitor various weather parameters in real-time through their Ecowitt weather station.

DANGER: This is a work in progress and should not be used in production.


## Features
- Real-time weather data collection from Ecowitt weather stations
- Support for multiple weather parameters:
  - Temperature
  - Humidity
  - Barometric pressure
  - Wind speed and direction
  - Rainfall
  - UV index
  - Solar radiation (if supported by your model)
- Data visualization and display
- Historical data storage

## Prerequisites
- Ecowitt weather station
- Python 3.7 or higher
- Network connectivity
- Ecowitt device configured and connected to your (local network)

## Installation

pip install -r requirements.txt

## Running the server
python backend/server.py

## Running the frontend
python frontend/app.py