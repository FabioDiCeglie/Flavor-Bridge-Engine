from urllib.parse import urlparse
from workers import Response, Request
from routes import health_check, seed, search, explain, docs, openapi_json


async def on_fetch(request: Request, env) -> Response:
    path = urlparse(request.url).path
    method = request.method
    
    # Documentation
    if path == "/docs":
        return await docs()
    
    if path == "/openapi.json":
        return await openapi_json()
    
    # Health check
    if path == "/health":
        return await health_check()
    
    # Seed database (POST only)
    if path == "/seed" and method == "POST":
        return await seed(env)
    
    # Search for ingredients
    if path == "/search" and method == "GET":
        return await search(env, request)

    if path == "/explain" and method == "POST":
        return await explain(env, request)
    
    return Response("Not Found", status=404)
