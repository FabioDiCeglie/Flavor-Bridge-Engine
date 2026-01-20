from urllib.parse import urlparse
from workers import Response, Request
from routes import health_check


async def on_fetch(request: Request) -> Response:
    path = urlparse(request.url).path
    
    if path == "/health":
        return await health_check()
    
    return Response("Not Found", status=404)
