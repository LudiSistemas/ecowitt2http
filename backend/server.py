from aiohttp import web
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcowittServer:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        self.app.router.add_post("/data/report", self.handle_report)
        self.app.router.add_get("/data/report", self.handle_report)

    async def handle_report(self, request):
        """Handle incoming data from Ecowitt devices."""
        try:
            if request.method == "POST":
                data = await request.post()
            else:  # GET
                data = request.query

            logger.info(f"Received data: {dict(data)}")
            
            # TODO: Process the data here
            
            return web.Response(text="OK")
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.Response(text="Error", status=500)

    def run(self):
        """Start the server."""
        web.run_app(self.app, host=self.host, port=self.port)

if __name__ == "__main__":
    server = EcowittServer()
    server.run()
