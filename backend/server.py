from aiohttp import web
import logging
import yaml
import aiohttp
import asyncio
from data_handler import WeatherDataHandler
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcowittServer:
    def __init__(self, config_path="config.yml"):
        self.config = self.load_config(config_path)
        self.host = self.config["server"]["host"]
        self.port = self.config["server"]["port"]
        self.app = web.Application()
        self.setup_routes()
        self.client_session = None
        self.data_handler = WeatherDataHandler(self.config)

    def load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def setup_routes(self):
        self.app.router.add_post("/data/report", self.handle_report)
        self.app.router.add_get("/data/report", self.handle_report)
        self.app.router.add_get("/api/weather/current", self.get_current_data)
        self.app.router.add_get("/api/weather/history", self.get_historical_data)
        
    async def relay_data(self, data):
        """Relay data to target server."""
        if not self.config["relay"]["enabled"]:
            return

        if self.client_session is None:
            self.client_session = aiohttp.ClientSession()

        target_url = f"http://{self.config['relay']['target_host']}:{self.config['relay']['target_port']}{self.config['relay']['target_path']}"
        
        try:
            async with self.client_session.request(
                method="POST",
                url=target_url,
                data=data
            ) as response:
                logger.info(f"Relay response status: {response.status}")
                return await response.text()
        except Exception as e:
            logger.error(f"Error relaying data: {e}")

    async def handle_report(self, request):
        """Handle incoming data from Ecowitt devices."""
        try:
            if request.method == "POST":
                data = await request.post()
            else:  # GET
                data = request.query

            logger.info(f"Received data: {dict(data)}")
            
            # Process and store data
            processed_data = await self.data_handler.process_data(dict(data))
            
            # Relay data if enabled
            if self.config["relay"]["enabled"]:
                await self.relay_data(data)
            
            return web.Response(text="OK")
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.Response(text="Error", status=500)

    async def cleanup(self):
        """Cleanup resources."""
        if self.client_session:
            await self.client_session.close()

    def run(self):
        """Start the server."""
        if not self.config["server"]["enabled"]:
            logger.info("Server is disabled in config")
            return

        try:
            web.run_app(self.app, host=self.host, port=self.port)
        finally:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.cleanup())

    async def start(self):
        """Initialize the server"""
        await self.data_handler.init()

    async def get_current_data(self, request):
        """Get most recent weather data"""
        data = await self.data_handler.get_data(
            datetime.now() - timedelta(minutes=5)
        )
        return web.json_response(data[0] if data else {})

    async def get_historical_data(self, request):
        """Get historical weather data"""
        start = request.query.get('start')
        end = request.query.get('end')
        
        try:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end) if end else None
            
            data = await self.data_handler.get_data(start_time, end_time)
            return web.json_response(data)
            
        except ValueError:
            return web.Response(
                text="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
                status=400
            )

if __name__ == "__main__":
    server = EcowittServer()
    server.run()
