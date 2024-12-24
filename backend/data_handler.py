from datetime import datetime
import json
import asyncio
import asyncpg
import aiomqtt
import logging

logger = logging.getLogger(__name__)

class WeatherDataHandler:
    def __init__(self, config):
        self.config = config
        self.mqtt_client = None
        self.db_pool = None

    async def init(self):
        """Initialize connections"""
        if self.config["mqtt"]["enabled"]:
            self.mqtt_client = aiomqtt.Client(
                hostname=self.config["mqtt"]["host"],
                port=self.config["mqtt"]["port"],
                username=self.config["mqtt"]["username"],
                password=self.config["mqtt"]["password"]
            )
            await self.mqtt_client.connect()

        if self.config["database"]["type"] == "timescale":
            self.db_pool = await asyncpg.create_pool(
                host=self.config["database"]["host"],
                port=self.config["database"]["port"],
                database=self.config["database"]["database"],
                user=self.config["database"]["username"],
                password=self.config["database"]["password"]
            )
            await self.init_db()

    async def init_db(self):
        """Initialize database schema"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    time TIMESTAMPTZ NOT NULL,
                    sensor_id TEXT,
                    temperature FLOAT,
                    humidity FLOAT,
                    pressure FLOAT,
                    wind_speed FLOAT,
                    wind_direction FLOAT,
                    rain_rate FLOAT,
                    uv INTEGER,
                    solar_radiation FLOAT
                );
                
                SELECT create_hypertable('weather_data', 'time', if_not_exists => TRUE);
            """)

    async def process_data(self, data: dict):
        """Process incoming weather data"""
        timestamp = datetime.now()
        
        # Convert data to standardized format
        processed_data = self.standardize_data(data)
        
        # Store in MQTT if enabled
        if self.config["mqtt"]["enabled"]:
            await self.publish_mqtt(processed_data)
        
        # Store in database
        await self.store_data(timestamp, processed_data)
        
        return processed_data

    def standardize_data(self, data: dict) -> dict:
        """Convert Ecowitt data format to standardized format"""
        # Map Ecowitt fields to standard fields
        # This mapping needs to be adjusted based on your specific device
        return {
            "temperature": float(data.get("tempf", 0)),
            "humidity": float(data.get("humidity", 0)),
            "pressure": float(data.get("baromrelin", 0)),
            "wind_speed": float(data.get("windspeedmph", 0)),
            "wind_direction": float(data.get("winddir", 0)),
            "rain_rate": float(data.get("rainratein", 0)),
            "uv": int(data.get("uv", 0)),
            "solar_radiation": float(data.get("solarradiation", 0))
        }

    async def publish_mqtt(self, data: dict):
        """Publish data to MQTT"""
        if self.mqtt_client:
            topic = self.config["mqtt"]["topic"]
            await self.mqtt_client.publish(
                topic,
                payload=json.dumps(data).encode()
            )

    async def store_data(self, timestamp: datetime, data: dict):
        """Store data in database"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO weather_data (
                        time, temperature, humidity, pressure,
                        wind_speed, wind_direction, rain_rate,
                        uv, solar_radiation
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, timestamp, *data.values())

    async def get_data(self, start_time: datetime, end_time: datetime = None):
        """Retrieve data from database"""
        if not end_time:
            end_time = datetime.now()
            
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM weather_data
                WHERE time BETWEEN $1 AND $2
                ORDER BY time DESC
            """, start_time, end_time)
            
        return [dict(row) for row in rows]

    async def cleanup(self):
        """Cleanup connections"""
        if self.mqtt_client:
            await self.mqtt_client.disconnect()
        if self.db_pool:
            await self.db_pool.close() 