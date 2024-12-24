from flask import Flask, render_template
import plotly.express as px
import plotly.utils
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

async def fetch_weather_data(endpoint, params=None):
    """Fetch data from backend API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://app:8080/api/weather/{endpoint}', params=params) as response:
            return await response.json()

def create_line_chart(df, y_column, title):
    """Create a line chart using plotly"""
    fig = px.line(df, x='time', y=y_column, title=title)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    # Get current data and last 24 hours
    current_data = asyncio.run(fetch_weather_data('current'))
    
    end = datetime.now()
    start = end - timedelta(hours=24)
    
    historical_data = asyncio.run(fetch_weather_data(
        'history',
        {'start': start.isoformat(), 'end': end.isoformat()}
    ))
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(historical_data)
    df['time'] = pd.to_datetime(df['time'])
    
    # Create charts
    temp_chart = create_line_chart(df, 'temperature', 'Temperature History')
    humidity_chart = create_line_chart(df, 'humidity', 'Humidity History')
    pressure_chart = create_line_chart(df, 'pressure', 'Pressure History')
    wind_chart = create_line_chart(df, 'wind_speed', 'Wind Speed History')
    
    return render_template('index.html',
                         current=current_data,
                         temp_chart=temp_chart,
                         humidity_chart=humidity_chart,
                         pressure_chart=pressure_chart,
                         wind_chart=wind_chart)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 