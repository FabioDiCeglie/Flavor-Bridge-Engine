from workers import Response, Request

RATE_LIMIT = 10
RATE_WINDOW = 60  # seconds


async def check_rate_limit(env, request: Request) -> Response | None:
    """
    Check rate limit for request. 
    Returns 429 Response if blocked, None if allowed.
    """
    ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For")
    if not ip:
        return None
    
    key = f"rate:{ip}"
    count = await env.RATE_LIMIT.get(key)
    
    if count and int(count) >= RATE_LIMIT:
        return Response(
            '{"error": "Too many requests. Please try again later."}',
            status=429,
            headers={"Content-Type": "application/json", "Retry-After": str(RATE_WINDOW)},
        )
    
    # Increment counter (only set TTL on first request)
    if count:
        await env.RATE_LIMIT.put(key, str(int(count) + 1))
    else:
        await env.RATE_LIMIT.put(key, "1", expiration_ttl=RATE_WINDOW)
    return None
