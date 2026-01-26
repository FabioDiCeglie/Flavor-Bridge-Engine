from urllib.parse import urlparse
from workers import Response, Request
from routes import health_check, seed, search, explain, docs, openapi_json
from utils import check_rate_limit

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def with_cors(response: Response) -> Response:
    """Add CORS headers to a response."""
    headers = dict(response.headers) if response.headers else {}
    headers.update(CORS_HEADERS)
    return Response(response.body, status=response.status, headers=headers)


async def on_fetch(request: Request, env) -> Response:
    path = urlparse(request.url).path
    method = request.method
    
    # CORS preflight
    if method == "OPTIONS":
        return Response("", status=204, headers=CORS_HEADERS)
    
    # Documentation
    if path == "/docs":
        return with_cors(await docs())
    if path == "/openapi.json":
        return with_cors(await openapi_json())
    
    # Health check
    if path == "/health":
        return with_cors(await health_check())
    
    # Seed database
    if path == "/seed" and method == "POST":
        return with_cors(await seed(env))
    
    # Search for ingredients (rate limited)
    if path == "/search" and method == "GET":
        if blocked := await check_rate_limit(env, request):
            return with_cors(blocked)
        return with_cors(await search(env, request))

    # Explain flavor bridges (rate limited)
    if path == "/explain" and method == "POST":
        if blocked := await check_rate_limit(env, request):
            return with_cors(blocked)
        return with_cors(await explain(env, request))
    
    return with_cors(Response("Not Found", status=404))
