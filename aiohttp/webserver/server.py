import aiohttp
from aiohttp import web
import asyncio

class WebServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.app = web.Application()
        routes = web.RouteTableDef()
        self.routes = routes

        @routes.get("/")
        async def index(request):
            return web.Response(text="Hello, World!")

        self.app.add_routes(routes)

    async def run(self):
        print(f"Starting server on {self.host}:{self.port}")

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        print(f"Server is running on {self.host}:{self.port}")

async def publish_loop():
    import time
    while True:
        print("Publishing message")
        time.sleep(1)


async def run(server: WebServer):
    await asyncio.gather(server.run(), publish_loop())


if __name__ == "__main__":
    asyncio_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(asyncio_loop)

    server = WebServer(host="0.0.0.0", port=8999)

    try:
        asyncio_loop.run_until_complete(run(server))

    except KeyboardInterrupt:
        print("Server is shutting down...")
