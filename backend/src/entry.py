from urllib.parse import urlparse
from workers import Response, Request
from routes import health_check, seed


async def on_fetch(request: Request, env) -> Response:
    path = urlparse(request.url).path
    method = request.method
    
    # Health check
    if path == "/health":
        return await health_check()
    
    # Seed database (POST only)
    if path == "/seed" and method == "POST":
        return await seed(env)
    
    return Response("Not Found", status=404)
