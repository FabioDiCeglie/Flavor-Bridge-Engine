import json
import hashlib
from workers import Response
from services import AIService, CacheService
from prompts import build_explain_prompt


async def explain(env, request) -> Response:
    """Explain why ingredients are chemical cousins using AI."""
    try:
        text = await request.text()
        body = json.loads(text)
        query = body.get("query")
        matches = body.get("matches")

        if not query or not matches:
            return Response(
                json.dumps({"error": "Missing 'query' or 'matches' in request body"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Create hash from match names only for cache key
        match_names = ",".join(sorted(m["name"].lower() for m in matches))
        matches_hash = hashlib.md5(match_names.encode()).hexdigest()[:8]

        # Check cache first
        cache_service = CacheService(env.CACHE)
        cached = await cache_service.get_explain(query, matches_hash)
        if cached:
            return Response(
                json.dumps(cached),
                headers={"Content-Type": "application/json", "X-Cache": "HIT"},
            )

        prompt = build_explain_prompt(query, matches)

        service = AIService(env.AI)
        explanation = await service.generate(prompt)

        response_data = {"query": query, "explanation": explanation}

        # Cache the result (24 hour TTL)
        await cache_service.set_explain(query, matches_hash, response_data)

        return Response(
            json.dumps(response_data),
            headers={"Content-Type": "application/json", "X-Cache": "MISS"},
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
